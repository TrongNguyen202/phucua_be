from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):

    phone = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    avatar = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "phone",
            "address",
            "avatar"
        ]

    def create(self, validated_data):

        phone = validated_data.pop("phone", "")
        address = validated_data.pop("address", "")
        avatar = validated_data.pop("avatar", None)

        user = User.objects.create_user(**validated_data)

        UserProfile.objects.create(
            user=user,
            phone=phone,
            address=address,
            avatar=avatar
        )

        return user