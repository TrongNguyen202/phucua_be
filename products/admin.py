from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "category",
        "base_price",
        "is_active",
        "created_at",
    )

    list_filter = ("category", "is_active", "is_featured")

    search_fields = ("name",)

    prepopulated_fields = {"slug": ("name",)}