from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model         = OrderItem
    extra         = 0
    fields        = ["variant", "product_name", "variant_sku", "unit_price", "quantity", "subtotal"]
    readonly_fields = ["subtotal"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ["id", "user", "status", "total", "shipping_fee", "created_at"]
    list_filter     = ["status", "created_at"]
    search_fields   = ["user__username", "shipping_full_name", "shipping_phone"]
    readonly_fields = ["subtotal", "total", "created_at", "updated_at"]
    inlines         = [OrderItemInline]

    # Cho phép đổi status trực tiếp từ list view
    list_editable   = ["status"]

    fieldsets = (
        ("Thông tin đơn hàng", {
            "fields": ("user", "status", "note")
        }),
        ("Địa chỉ giao hàng", {
            "fields": (
                "shipping_full_name", "shipping_phone", "shipping_address",
                "shipping_city", "shipping_district", "shipping_ward"
            )
        }),
        ("Thanh toán", {
            "fields": ("shipping_fee", "discount_amount", "subtotal", "total")
        }),
        ("Thời gian", {
            "fields": ("created_at", "updated_at")
        }),
    )