from django.contrib import admin
from .models import Product
from variants.admin import ProductVariantInline


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display        = ["name", "category", "base_price", "is_active", "is_featured", "created_at"]
    list_filter         = ["is_active", "is_featured", "category"]
    search_fields       = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields     = ["created_at", "updated_at"]
    inlines             = [ProductVariantInline]