import logging
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order, OrderItem
from .serializers import OrderSerializer, CreateOrderSerializer
from cart.models import Cart

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class   = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related("items__variant__product", "items__variant__size", "items__variant__color")
        )

    @action(detail=False, methods=["post"])
    def checkout(self, request):

        # Truyền request vào context để validate address
        serializer = CreateOrderSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        address      = serializer.validated_data["address_id"]
        note         = serializer.validated_data["note"]
        shipping_fee = serializer.validated_data["shipping_fee"]

        # Lấy cart
        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            return Response({"detail": "Giỏ hàng trống."}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart.items.select_related(
            "variant__product",
            "variant__size",
            "variant__color"
        ).all()

        if not cart_items.exists():
            return Response({"detail": "Giỏ hàng trống."}, status=status.HTTP_400_BAD_REQUEST)

        # Kiểm tra tồn kho trước khi tạo order
        errors = []
        for item in cart_items:
            if not item.variant.is_active:
                errors.append(f"'{item.variant}' hiện không còn bán.")
            elif item.variant.stock < item.quantity:
                errors.append(
                    f"'{item.variant}' chỉ còn {item.variant.stock} sản phẩm, "
                    f"bạn đang chọn {item.quantity}."
                )
        if errors:
            return Response({"detail": errors}, status=status.HTTP_400_BAD_REQUEST)

        # Dùng transaction để đảm bảo toàn vẹn dữ liệu
        with transaction.atomic():

            order = Order.objects.create(
                user               = request.user,
                shipping_full_name = address.full_name,
                shipping_phone     = address.phone,
                shipping_address   = address.address,
                shipping_city      = address.city,
                shipping_district  = address.district,
                shipping_ward      = address.ward,
                note               = note,
                shipping_fee       = shipping_fee,
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order        = order,
                    variant      = item.variant,
                    product_name = item.variant.product.name,
                    variant_sku  = item.variant.sku,
                    unit_price   = item.variant.price,
                    quantity     = item.quantity,
                )

                # Trừ tồn kho
                item.variant.stock -= item.quantity
                item.variant.save(update_fields=["stock"])

            # Xoá cart sau khi đặt hàng thành công
            cart.items.all().delete()

        logger.info(f"Order #{order.pk} tạo thành công bởi user #{request.user.pk}")

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.status not in [Order.Status.PENDING, Order.Status.CONFIRMED]:
            return Response(
                {"detail": "Không thể huỷ đơn ở trạng thái này."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Hoàn lại tồn kho
            for item in order.items.select_related("variant"):
                item.variant.stock += item.quantity
                item.variant.save(update_fields=["stock"])

            order.status = Order.Status.CANCELLED
            order.save()

        return Response(OrderSerializer(order).data)