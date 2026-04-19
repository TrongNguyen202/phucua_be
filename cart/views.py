from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


def get_or_create_cart(request):
    """Lấy hoặc tạo cart dựa theo user (đã login) hoặc session (guest)."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


class CartViewSet(viewsets.GenericViewSet):

    serializer_class = CartSerializer

    # cart/views.py
    def get_queryset(self):
        return Cart.objects.prefetch_related(
            "items__variant__product__category",  # ← prefetch đủ
            "items__variant__size",
            "items__variant__color",
            "items__variant__image",
        ).all()

    # GET /cart/
    @action(detail=False, methods=["get"])
    def me(self, request):
        cart = get_or_create_cart(request)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    # POST /cart/add/
    @action(detail=False, methods=["post"])
    def add(self, request):
        cart = get_or_create_cart(request)

        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        variant = serializer.validated_data["variant"]  # ← đổi từ product → variant
        quantity = serializer.validated_data.get("quantity", 1)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,  # ← đổi
            defaults={"quantity": quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    # PATCH /cart/update/{item_id}/
    @action(detail=False, methods=["patch"], url_path="update/(?P<item_id>[^/.]+)")
    def update_item(self, request, item_id=None):
        cart = get_or_create_cart(request)

        try:
            item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        quantity = request.data.get("quantity")

        if quantity is None or int(quantity) < 1:
            return Response({"detail": "Quantity must be >= 1."}, status=status.HTTP_400_BAD_REQUEST)

        item.quantity = int(quantity)
        item.save()

        return Response(CartSerializer(cart).data)

    # DELETE /cart/remove/{item_id}/
    @action(detail=False, methods=["delete"], url_path="remove/(?P<item_id>[^/.]+)")
    def remove_item(self, request, item_id=None):
        cart = get_or_create_cart(request)

        try:
            item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()

        return Response(CartSerializer(cart).data)

    # DELETE /cart/clear/
    @action(detail=False, methods=["delete"])
    def clear(self, request):
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        return Response(CartSerializer(cart).data)