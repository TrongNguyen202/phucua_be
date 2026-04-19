from rest_framework import serializers
from .models import Cart, CartItem
from variants.models import ProductVariant


class ProductInCartSerializer(serializers.Serializer):
    """Thông tin product cần thiết trong cart."""
    id          = serializers.IntegerField()
    name        = serializers.CharField()
    thumbnail   = serializers.URLField()
    slug        = serializers.SlugField()
    category    = serializers.SerializerMethodField()

    def get_category(self, obj):
        return {"id": obj.category.id, "name": obj.category.name} if obj.category else None


class SizeInCartSerializer(serializers.Serializer):
    id   = serializers.IntegerField()
    name = serializers.CharField()


class ColorInCartSerializer(serializers.Serializer):
    id       = serializers.IntegerField()
    name     = serializers.CharField()
    hex_code = serializers.CharField()


class VariantInCartSerializer(serializers.Serializer):
    """Variant đầy đủ thông tin dùng trong cart."""
    id      = serializers.IntegerField()
    sku     = serializers.CharField()
    price   = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock   = serializers.IntegerField()
    image   = serializers.URLField(allow_null=True, allow_blank=True)
    size    = SizeInCartSerializer()
    color   = ColorInCartSerializer()
    product = ProductInCartSerializer()


class CartItemSerializer(serializers.ModelSerializer):

    variant    = VariantInCartSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source="variant",
        write_only=True
    )
    quantity = serializers.IntegerField(default=1, min_value=1)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model  = CartItem
        fields = ["id", "variant", "variant_id", "quantity", "subtotal", "added_at"]
        read_only_fields = ["id", "added_at"]


class CartSerializer(serializers.ModelSerializer):

    items       = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Cart
        fields = ["id", "items", "total_price", "total_items", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]