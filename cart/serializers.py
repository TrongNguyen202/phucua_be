from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product          # ← thiếu dòng này



class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )
    quantity = serializers.IntegerField(default=1, min_value=1)

    class Meta:
        model = CartItem
        fields = ["product", "quantity"]

class CartSerializer(serializers.ModelSerializer):

    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price", "total_items", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]