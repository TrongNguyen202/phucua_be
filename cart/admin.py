from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model           = CartItem
    extra           = 0
    fields          = ["variant", "quantity", "get_subtotal"]
    readonly_fields = ["get_subtotal"]

    def get_subtotal(self, obj):
        return f"{obj.subtotal:,.0f}₫"
    get_subtotal.short_description = "Tạm tính"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display    = ["id", "user", "session_key", "get_total_items", "get_total_price", "updated_at"]
    search_fields   = ["user__username", "session_key"]
    readonly_fields = ["get_total_price", "get_total_items"]
    inlines         = [CartItemInline]

    def get_total_price(self, obj):
        return f"{obj.total_price:,.0f}₫"
    get_total_price.short_description = "Tổng tiền"

    def get_total_items(self, obj):
        return obj.total_items
    get_total_items.short_description = "Số sản phẩm"