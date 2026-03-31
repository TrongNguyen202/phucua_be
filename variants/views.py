from rest_framework import viewsets
from .models import Size, Color, ProductVariant
from .serializers import SizeSerializer, ColorSerializer, ProductVariantSerializer


class SizeViewSet(viewsets.ModelViewSet):
    queryset         = Size.objects.all()
    serializer_class = SizeSerializer


class ColorViewSet(viewsets.ModelViewSet):
    queryset         = Color.objects.all()
    serializer_class = ColorSerializer


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset         = ProductVariant.objects.select_related("product", "size", "color").all()
    serializer_class = ProductVariantSerializer

    def get_queryset(self):
        queryset    = super().get_queryset()
        product_id  = self.request.query_params.get("product")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset