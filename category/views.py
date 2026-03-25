from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category
from .serializers import CategorySerializer
from products.models import Product
from products.serializers  import ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"

    @action(detail=True, methods=["get"])
    def products(self, request, slug=None):

        category = self.get_object()

        products = Product.objects.filter(category=category)

        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)