# accounts/serializers.py — bỏ UserProfileSerializer, chỉ giữ Address + cập nhật UserSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Address
        fields = [
            "id", "full_name", "phone", "address",
            "city", "district", "ward", "postal_code",
            "address_type", "is_default", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    # Lấy profile từ app users
    phone  = serializers.CharField(source="userprofile.phone",   read_only=True)
    avatar = serializers.URLField(source="userprofile.avatar",   read_only=True)

    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model  = User
        fields = ["id", "username", "email", "first_name", "last_name", "phone", "avatar", "addresses"]
        read_only_fields = ["id"]