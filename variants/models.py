from django.db import models
from products.models import Product


class Size(models.Model):
    name  = models.CharField(max_length=10)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Color(models.Model):
    name     = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return f"{self.name} ({self.hex_code})"


class ProductType(models.Model):  # ← thêm model mới
    name = models.CharField(max_length=50)  # T-Shirt, Sweatshirt, Hoodie

    def __str__(self):
        return self.name


class ProductVariant(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size    = models.ForeignKey(Size,  on_delete=models.PROTECT, null=True, blank=True)
    color   = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, blank=True)
    type    = models.ForeignKey(       # ← thêm field mới
        ProductType,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="variants"
    )

    sku            = models.CharField(max_length=100, unique=True)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock          = models.PositiveIntegerField(default=0)
    image          = models.URLField(blank=True)
    is_active      = models.BooleanField(default=True)

    class Meta:
        unique_together = ("product", "size", "color", "type")  # ← thêm type
        indexes = [
            models.Index(fields=["product", "is_active"]),
        ]

    @property
    def price(self):
        return self.price_override or self.product.base_price

    @property
    def in_stock(self):
        return self.stock > 0

    def __str__(self):
        parts = [self.product.name]
        if self.type:  parts.append(self.type.name)
        if self.size:  parts.append(self.size.name)
        if self.color: parts.append(self.color.name)
        return " - ".join(parts)