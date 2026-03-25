from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()


class Cart(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart"
    )

    session_key = models.CharField(max_length=40, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

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
        owner = self.user or self.session_key
        return f"Cart ({owner})"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    quantity = models.PositiveIntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product")
        indexes = [
            models.Index(fields=["cart", "product"]),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.base_price * self.quantity