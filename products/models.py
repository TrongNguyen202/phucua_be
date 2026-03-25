from django.db import models
from django.utils.text import slugify
from category.models import Category

# Create your models here.
class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    name = models.CharField(max_length=255)

    slug = models.SlugField(unique=True)

    description = models.TextField()

    short_description = models.TextField(blank=True)

    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    thumbnail = models.URLField()

    meta_title = models.CharField(max_length=255, blank=True)

    meta_description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
        ]

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name