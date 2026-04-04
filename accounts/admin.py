# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Address   # ← bỏ UserProfile

User = get_user_model()


class AddressInline(admin.TabularInline):
    model  = Address
    extra  = 0
    fields = ["full_name", "phone", "address", "city", "district", "ward", "address_type", "is_default"]


class UserAdmin(BaseUserAdmin):
    inlines = [AddressInline]   # ← bỏ UserProfileInline


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "phone", "city", "district", "address_type", "is_default", "user"]
    list_filter   = ["address_type", "is_default", "city"]
    search_fields = ["full_name", "phone", "user__username"]