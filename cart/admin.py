from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model         = CartItem
    extra         = 0
    fields        = ["variant", "quantity", "subtotal"]
    readonly_fields = ["subtotal"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display    = ["id", "user", "session_key", "total_items", "total_price", "updated_at"]
    search_fields   = ["user__username", "session_key"]
    readonly_fields = ["total_price", "total_items"]
    inlines         = [CartItemInline]