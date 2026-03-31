# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile, Address

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0


class AddressInline(admin.TabularInline):
    model  = Address
    extra  = 0
    fields = ["full_name", "phone", "address", "city", "district", "ward", "address_type", "is_default"]


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline, AddressInline]


admin.site.unregister(User)   # ← unregister bản mặc định
admin.site.register(User, UserAdmin)  # ← register lại với custom