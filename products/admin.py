from django.contrib import admin
from .models import Product, ProductImage
from variants.admin import ProductVariantInline


class ProductImageInline(admin.TabularInline):
    model   = ProductImage
    extra   = 3
    fields  = ["image", "alt_text", "order"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display        = ["name", "category", "base_price", "is_active", "is_featured", "created_at"]
    list_filter         = ["is_active", "is_featured", "category"]
    search_fields       = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields     = ["created_at", "updated_at"]
    inlines             = [ProductImageInline, ProductVariantInline]  # ← thêm


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display  = ["product", "order", "image"]
    list_filter   = ["product"]
    ordering      = ["product", "order"]