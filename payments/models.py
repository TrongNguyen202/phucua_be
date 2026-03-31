from django.db import models
from orders.models import Order


class Payment(models.Model):

    class Method(models.TextChoices):
        SEPAY = "sepay", "SePay (Chuyển khoản)"
        COD   = "cod",   "Thanh toán khi nhận hàng"

    class Status(models.TextChoices):
        PENDING  = "pending",  "Chờ thanh toán"
        PAID     = "paid",     "Đã thanh toán"
        FAILED   = "failed",   "Thất bại"
        REFUNDED = "refunded", "Đã hoàn tiền"

    order          = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    method         = models.CharField(max_length=20, choices=Method.choices)
    status         = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    amount         = models.DecimalField(max_digits=12, decimal_places=2)

    # Mã thanh toán user ghi vào nội dung chuyển khoản, vd: SHOP123
    payment_code   = models.CharField(max_length=50, unique=True, blank=True)

    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Tự sinh payment_code từ order_id nếu chưa có
        if not self.payment_code and self.order_id:
            self.payment_code = f"SHOP{self.order_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment #{self.pk} | {self.payment_code} | {self.status}"


class SePayTransaction(models.Model):
    """Lưu raw webhook payload từ SePay để đối soát."""

    payment          = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="sepay_transactions"
    )

    # Các field từ SePay webhook payload
    sepay_id         = models.BigIntegerField(unique=True)
    gateway          = models.CharField(max_length=100)
    transaction_date = models.DateTimeField()
    account_number   = models.CharField(max_length=100)
    sub_account      = models.CharField(max_length=250, blank=True, null=True)
    transfer_type    = models.CharField(max_length=10)   # "in" | "out"
    transfer_amount  = models.DecimalField(max_digits=14, decimal_places=2)
    accumulated      = models.DecimalField(max_digits=14, decimal_places=2)
    code             = models.CharField(max_length=250, blank=True, null=True)
    content          = models.TextField(blank=True)
    reference_code   = models.CharField(max_length=255, blank=True)
    description      = models.TextField(blank=True)

    raw_payload      = models.JSONField(default=dict)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SePay Tx {self.sepay_id} | {self.transfer_amount}đ | code={self.code}"