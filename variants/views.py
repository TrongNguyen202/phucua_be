from rest_framework import viewsets
from .models import Size, Color, ProductType, ProductVariant
from .serializers import SizeSerializer, ColorSerializer, ProductTypeSerializer, ProductVariantSerializer


class SizeViewSet(viewsets.ModelViewSet):
    queryset         = Size.objects.all()
    serializer_class = SizeSerializer


class ColorViewSet(viewsets.ModelViewSet):
    queryset         = Color.objects.all()
    serializer_class = ColorSerializer


class ProductTypeViewSet(viewsets.ModelViewSet):   # ← thêm
    queryset         = ProductType.objects.all()
    serializer_class = ProductTypeSerializer


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset         = ProductVariant.objects.select_related(
        "product", "size", "color", "type"   # ← thêm type
    ).all()
    serializer_class = ProductVariantSerializer

    def get_queryset(self):
        queryset   = super().get_queryset()
        product_id = self.request.query_params.get("product")
        type_id    = self.request.query_params.get("type")   # ← filter theo type
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if type_id:
            queryset = queryset.filter(type_id=type_id)
        return queryset