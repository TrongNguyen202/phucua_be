import logging
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment, SePayTransaction
from .serializers import PaymentSerializer, CreatePaymentSerializer, SePayWebhookSerializer
from orders.models import Order

logger = logging.getLogger(__name__)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class   = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            order__user=self.request.user
        ).prefetch_related("sepay_transactions")

    @action(detail=False, methods=["post"])
    def create_payment(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = Order.objects.get(
                id=serializer.validated_data["order_id"],
                user=request.user
            )
        except Order.DoesNotExist:
            return Response({"detail": "Không tìm thấy đơn hàng."}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(order, "payment"):
            return Response({"detail": "Đơn hàng đã có thanh toán."}, status=status.HTTP_400_BAD_REQUEST)

        payment = Payment.objects.create(
            order  = order,
            method = serializer.validated_data["method"],
            amount = order.total,
        )

        # COD → confirm luôn
        if payment.method == Payment.Method.COD:
            payment.status = Payment.Status.PAID
            payment.save()
            order.status = Order.Status.CONFIRMED
            order.save()

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class SePayWebhookView(APIView):
    """
    POST /api/payments/sepay-webhook/
    Endpoint nhận webhook từ SePay.
    Cấu hình trên dashboard SePay: Authentication = Api Key.
    """

    permission_classes = []  # Public — xác thực bằng API Key header

    def _verify_api_key(self, request) -> bool:
        auth_header = request.headers.get("Authorization", "")
        expected    = f"Apikey {settings.SEPAY_WEBHOOK_API_KEY}"
        return auth_header == expected

    def post(self, request):

        # 1. Xác thực API Key
        if not self._verify_api_key(request):
            logger.warning("SePay webhook: API Key không hợp lệ")
            return Response({"success": False}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. Validate payload
        serializer = SePayWebhookSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"SePay webhook payload lỗi: {serializer.errors}")
            return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # 3. Bỏ qua giao dịch chuyển tiền ra
        if data["transferType"] != "in":
            return Response({"success": True}, status=status.HTTP_200_OK)

        # 4. Tránh xử lý duplicate
        if SePayTransaction.objects.filter(sepay_id=data["id"]).exists():
            logger.info(f"SePay Tx {data['id']} đã xử lý, bỏ qua.")
            return Response({"success": True}, status=status.HTTP_200_OK)

        # 5. Tìm Payment theo payment_code
        payment_code = data.get("code")
        payment      = None

        if payment_code:
            try:
                payment = Payment.objects.select_related("order").get(
                    payment_code=payment_code,
                    method=Payment.Method.SEPAY,
                )
            except Payment.DoesNotExist:
                logger.warning(f"SePay webhook: Không tìm thấy payment với code={payment_code}")

        # 6. Lưu transaction
        SePayTransaction.objects.create(
            payment          = payment,
            sepay_id         = data["id"],
            gateway          = data["gateway"],
            transaction_date = data["transactionDate"],
            account_number   = data["accountNumber"],
            sub_account      = data.get("subAccount"),
            transfer_type    = data["transferType"],
            transfer_amount  = data["transferAmount"],
            accumulated      = data["accumulated"],
            code             = payment_code,
            content          = data["content"],
            reference_code   = data["referenceCode"],
            description      = data["description"],
            raw_payload      = request.data,
        )

        # 7. Cập nhật trạng thái nếu khớp payment
        if payment and payment.status == Payment.Status.PENDING:

            # Kiểm tra số tiền đủ không (cho phép sai lệch 1000đ)
            if data["transferAmount"] >= payment.amount - 1000:
                payment.status       = Payment.Status.PAID
                payment.save()

                payment.order.status = Order.Status.CONFIRMED
                payment.order.save()

                logger.info(f"Đơn hàng #{payment.order_id} đã thanh toán qua SePay.")
            else:
                logger.warning(
                    f"SePay Tx {data['id']}: Số tiền {data['transferAmount']} "
                    f"< {payment.amount} (thiếu tiền)"
                )

        # 8. Response đúng chuẩn SePay yêu cầu
        return Response({"success": True}, status=status.HTTP_200_OK)