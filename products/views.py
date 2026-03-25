from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.select_related("category").all()
    serializer_class = ProductSerializer
    lookup_field = "slug"

    filter_backends = [DjangoFilterBackend, SearchFilter]

    filterset_fields = ["category", "is_featured"]
    search_fields = ["name", "description"]

    def get_queryset(self):

        queryset = super().get_queryset()

        category_slug = self.request.query_params.get("category")

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        return queryset

    @action(detail=False, methods=["get"])
    def featured(self, request):

        products = Product.objects.filter(is_featured=True)

        serializer = self.get_serializer(products, many=True)

        return Response(serializer.data)