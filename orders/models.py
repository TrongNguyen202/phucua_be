from django.db import models
from django.contrib.auth import get_user_model
from variants.models import ProductVariant
from accounts.models import Address
from decimal import Decimal
User = get_user_model()


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING    = "pending",    "Pending"
        CONFIRMED  = "confirmed",  "Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED    = "shipped",    "Shipped"
        DELIVERED  = "delivered",  "Delivered"
        CANCELLED  = "cancelled",  "Cancelled"
        REFUNDED   = "refunded",   "Refunded"

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="orders",
        null=True, blank=True
    )

    # Snapshot địa chỉ tại thời điểm đặt hàng
    shipping_full_name = models.CharField(max_length=255)
    shipping_phone     = models.CharField(max_length=20)
    shipping_address   = models.TextField()
    shipping_city      = models.CharField(max_length=100)
    shipping_district  = models.CharField(max_length=100)
    shipping_ward      = models.CharField(max_length=100)

    status         = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    note           = models.TextField(blank=True)
    shipping_fee   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["created_at"]),
        ]

    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total(self):
        return self.subtotal + self.shipping_fee - self.discount_amount

    def __str__(self):
        return f"Order #{self.pk} - {self.user} - {self.status}"


class OrderItem(models.Model):

    order   = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="order_items")

    # Snapshot giá tại thời điểm mua
    product_name = models.CharField(max_length=255)
    variant_sku  = models.CharField(max_length=100)
    unit_price   = models.DecimalField(max_digits=10, decimal_places=2)
    quantity     = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("order", "variant")

    @property
    def subtotal(self):
        return (self.unit_price or Decimal("0")) * (self.quantity or 0)

    def __str__(self):
        return f"{self.quantity}x {self.product_name} (Order #{self.order_id})"