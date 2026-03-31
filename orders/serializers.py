from rest_framework import serializers
from .models import Order, OrderItem
from variants.serializers import ProductVariantSerializer
from accounts.models import Address


class OrderItemSerializer(serializers.ModelSerializer):

    variant  = ProductVariantSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = OrderItem
        fields = ["id", "variant", "product_name", "variant_sku", "unit_price", "quantity", "subtotal"]


class OrderSerializer(serializers.ModelSerializer):

    items    = OrderItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total    = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = Order
        fields = [
            "id", "status", "note",
            "shipping_full_name", "shipping_phone", "shipping_address",
            "shipping_city", "shipping_district", "shipping_ward",
            "shipping_fee", "discount_amount",
            "subtotal", "total",
            "items", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at"]


class CreateOrderSerializer(serializers.Serializer):

    address_id   = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
    note         = serializers.CharField(required=False, allow_blank=True, default="")
    shipping_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)

    def validate_address_id(self, address):
        # Đảm bảo address thuộc về user đang request
        request = self.context.get("request")
        if address.user != request.user:
            raise serializers.ValidationError("Địa chỉ không hợp lệ.")
        return address