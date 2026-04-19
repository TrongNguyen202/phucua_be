from django.contrib import admin
from .models import Size, Color, ProductType, ProductVariant


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ["name", "order"]
    ordering     = ["order"]


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ["name", "hex_code"]


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


class ProductVariantInline(admin.TabularInline):
    model   = ProductVariant
    extra   = 0
    fields  = ["type", "size", "color", "sku", "price_override", "stock", "image", "is_active"]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display    = ["product", "type", "size", "color", "sku", "stock", "price", "is_active"]
    list_filter     = ["is_active", "type", "size", "color"]
    search_fields   = ["sku", "product__name"]
    readonly_fields = ["price", "in_stock"]