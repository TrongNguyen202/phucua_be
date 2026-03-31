from django.contrib import admin
from .models import Size, Color, ProductVariant


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ["name", "order"]
    ordering     = ["order"]


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ["name", "hex_code"]


class ProductVariantInline(admin.TabularInline):
    model  = ProductVariant
    extra  = 0
    fields = ["size", "color", "sku", "price_override", "stock", "is_active"]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display  = ["product", "size", "color", "sku", "stock", "price", "is_active"]
    list_filter   = ["is_active", "size", "color"]
    search_fields = ["sku", "product__name"]
    readonly_fields = ["price", "in_stock"]