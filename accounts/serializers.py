from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, Address

User = get_user_model()


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = [
            "id", "full_name", "phone", "address",
            "city", "district", "ward", "postal_code",
            "address_type", "is_default", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ["id", "phone", "avatar", "date_of_birth", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class UserSerializer(serializers.ModelSerializer):

    profile   = UserProfileSerializer(read_only=True)
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "profile", "addresses"]
        read_only_fields = ["id"]