from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):

    model = CartItem
    extra = 0
    readonly_fields = ["subtotal", "added_at"]
    fields = ["product", "quantity", "subtotal", "added_at"]

    def subtotal(self, obj):
        return f"{obj.subtotal:,.0f} ₫"
    subtotal.short_description = "Thành tiền"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = ["id", "owner", "total_items_display", "total_price_display", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user__username", "user__email", "session_key"]
    readonly_fields = ["total_price", "total_items", "created_at", "updated_at"]
    inlines = [CartItemInline]

    fieldsets = (
        ("Chủ sở hữu", {
            "fields": ("user", "session_key")
        }),
        ("Thống kê", {
            "fields": ("total_items", "total_price")
        }),
        ("Thời gian", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def owner(self, obj):
        if obj.user:
            return format_html(
                '<b>👤 {}</b>',
                obj.user.username
            )
        return format_html(
            '<span style="color: gray;">🔑 {}</span>',
            obj.session_key
        )
    owner.short_description = "Chủ giỏ hàng"

    def total_items_display(self, obj):
        return f"{obj.total_items} sản phẩm"
    total_items_display.short_description = "Số lượng"

    def total_price_display(self, obj):
        return format_html(
            '<span style="color: green; font-weight: bold;">{:,.0f} ₫</span>',
            obj.total_price
        )
    total_price_display.short_description = "Tổng tiền"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = ["id", "cart_owner", "product_link", "quantity", "subtotal_display", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["cart__user__username", "cart__session_key", "product__name"]
    readonly_fields = ["subtotal", "added_at"]
    autocomplete_fields = ["product"]

    fieldsets = (
        ("Thông tin", {
            "fields": ("cart", "product", "quantity")
        }),
        ("Chi tiết", {
            "fields": ("subtotal", "added_at"),
            "classes": ("collapse",)
        }),
    )

    def cart_owner(self, obj):
        if obj.cart.user:
            return obj.cart.user.username
        return f"Guest ({obj.cart.session_key[:8]}...)"
    cart_owner.short_description = "Giỏ của"

    def product_link(self, obj):
        return format_html(
            '<a href="/admin/products/product/{}/change/">{}</a>',
            obj.product.id,
            obj.product.name
        )
    product_link.short_description = "Sản phẩm"

    def subtotal_display(self, obj):
        return format_html(
            '<span style="color: green;">{:,.0f} ₫</span>',
            obj.subtotal
        )
    subtotal_display.short_description = "Thành tiền"