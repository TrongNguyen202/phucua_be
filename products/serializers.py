from rest_framework import serializers
from .models import Product, ProductImage
from category.serializers import CategorySerializer
from category.models import Category

from .utils import upload_image_to_imagur


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "order"]


class ProductSerializer(serializers.ModelSerializer):

    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )

    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    # upload files
    thumbnail_file = serializers.ImageField(
        write_only=True,
        required=False
    )

    product_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "category",
            "name",
            "slug",
            "description",
            "short_description",
            "base_price",

            "thumbnail",
            "thumbnail_file",

            "images",
            "product_images",

            "meta_title",
            "meta_description",
            "is_active",
            "is_featured",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["thumbnail"]

    def create(self, validated_data):

        thumbnail_file = validated_data.pop("thumbnail_file", None)

        product_images = validated_data.pop("product_images", [])

        # upload thumbnail
        thumbnail_url = ""

        if thumbnail_file:
            thumbnail_url = upload_image_to_imagur(
                thumbnail_file
            )

        validated_data["thumbnail"] = thumbnail_url

        product = Product.objects.create(**validated_data)

        # upload gallery images
        for index, image_file in enumerate(product_images):

            image_url = upload_image_to_imagur(image_file)

            ProductImage.objects.create(
                product=product,
                image=image_url,
                order=index
            )

        return product