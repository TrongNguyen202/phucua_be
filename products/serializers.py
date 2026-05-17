from rest_framework import serializers
from .models import Product, ProductImage
from category.models import Category
from variants.models import ProductVariant
from variants.serializers import ProductVariantSerializer

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "alt_text",
            "order"
        ]


class ProductSerializer(serializers.ModelSerializer):

    # ─── GET category object ─────────────────────
    category = serializers.SerializerMethodField(read_only=True)
    variants = ProductVariantSerializer(
        many=True,
        read_only=True
    )
    # ─── POST/PUT category_id ───────────────────
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True
    )

    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    # frontend gửi gallery images
    gallery_images = serializers.ListField(
        child=serializers.URLField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product

        # fields = [
        #     "id",
        #
        #     "category",
        #     "category_id",
        #
        #     "name",
        #     "slug",
        #     "description",
        #     "short_description",
        #     "base_price",
        #     "thumbnail",
        #
        #     "images",
        #     "gallery_images",
        #
        #     "meta_title",
        #     "meta_description",
        #
        #     "is_active",
        #     "is_featured",
        #
        #     "created_at",
        #     "updated_at",
        # ]
        fields = [
            "id",

            "category",
            "category_id",

            "name",
            "slug",
            "description",
            "short_description",
            "base_price",
            "thumbnail",
            "is_featured",
            "images",
            "gallery_images",

            "variants",

            "meta_title",
            "meta_description",

            "is_active",
            "is_featured",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "slug",
            "created_at",
            "updated_at"
        ]

    # ─────────────────────────────────────────────
    # Return category object
    # ─────────────────────────────────────────────
    def get_category(self, obj):
        if not obj.category:
            return None

        return {
            "id": obj.category.id,
            "name": obj.category.name
        }

    # ─────────────────────────────────────────────
    # CREATE
    # ─────────────────────────────────────────────
    def create(self, validated_data):

        gallery_images = validated_data.pop(
            "gallery_images",
            []
        )

        product = Product.objects.create(
            **validated_data
        )

        for index, image_url in enumerate(gallery_images):

            ProductImage.objects.create(
                product=product,
                image=image_url,
                order=index
            )

        return product

    # ─────────────────────────────────────────────
    # UPDATE
    # ─────────────────────────────────────────────
    # def update(self, instance, validated_data):
    #
    #     gallery_images = validated_data.pop(
    #         "gallery_images",
    #         None
    #     )
    #
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #
    #     instance.save()
    #
    #     # update gallery nếu frontend gửi lên
    #     if gallery_images is not None:
    #
    #         instance.images.all().delete()
    #
    #         for index, image_url in enumerate(gallery_images):
    #
    #             ProductImage.objects.create(
    #                 product=instance,
    #                 image=image_url,
    #                 order=index
    #             )
    #
    #     return instance
    def update(self, instance, validated_data):

        gallery_images = validated_data.pop(
            "gallery_images",
            None
        )

        variants_data = self.initial_data.get("variants", [])

        # update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # ─── update gallery ─────────────────────
        if gallery_images is not None:

            instance.images.all().delete()

            for index, image_url in enumerate(gallery_images):
                ProductImage.objects.create(
                    product=instance,
                    image=image_url,
                    order=index
                )

        # ─── update variants ────────────────────

        existing_variant_ids = []

        for variant_data in variants_data:

            variant_id = variant_data.get("id")

            payload = {
                "sku": variant_data.get("sku"),
                "size_id": variant_data.get("size_id") or None,
                "color_id": variant_data.get("color_id") or None,
                "type_id": variant_data.get("type_id") or None,
                "price_override": variant_data.get("price_override") or None,
                "stock": variant_data.get("stock", 0),
                "image": variant_data.get("image", ""),
                "is_active": variant_data.get("is_active", True),
            }

            # UPDATE
            if variant_id:

                try:
                    variant = ProductVariant.objects.get(
                        id=variant_id,
                        product=instance
                    )

                    for key, value in payload.items():
                        setattr(variant, key, value)

                    variant.save()

                    existing_variant_ids.append(variant.id)

                except ProductVariant.DoesNotExist:
                    pass

            # CREATE
            else:

                variant = ProductVariant.objects.create(
                    product=instance,
                    **payload
                )

                existing_variant_ids.append(variant.id)

        # DELETE variants removed on frontend
        instance.variants.exclude(
            id__in=existing_variant_ids
        ).delete()

        return instance