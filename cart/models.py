from django.db import models
from django.contrib.auth import get_user_model
from variants.models import ProductVariant   # ← đổi import

User = get_user_model()


class Cart(models.Model):

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        null=True, blank=True, related_name="cart"
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(user__isnull=False) |
                    models.Q(session_key__isnull=False)
                ),
                name="cart_must_have_user_or_session"
            )
        ]

    def __str__(self):
        return f"Cart ({self.user or self.session_key})"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):

    cart    = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(                          # ← đổi product → variant
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "variant")             # ← đổi
        indexes = [
            models.Index(fields=["cart", "variant"]),     # ← đổi
        ]

    def __str__(self):
        return f"{self.quantity}x {self.variant}"

    @property
    def subtotal(self):
        return self.variant.price * self.quantity         # ← đổi