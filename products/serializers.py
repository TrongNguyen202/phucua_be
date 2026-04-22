# products/serializers.py
from rest_framework import serializers
from .models import Product, ProductImage
from category.serializers import CategorySerializer  # ← dùng absolute import, bỏ dấu ..


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductImage
        fields = ["id", "image", "alt_text", "order"]


class ProductSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)
    images   = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model  = Product
        fields = [
            "id", "category", "name", "slug",
            "description", "short_description",
            "base_price", "thumbnail",
            "images",
            "meta_title", "meta_description",
            "is_active", "is_featured",
            "created_at", "updated_at",
        ]