from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import  Address
from .serializers import UserSerializer, AddressSerializer

User = get_user_model()


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /accounts/me/"""

    serializer_class  = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AddressViewSet(viewsets.ModelViewSet):
    """CRUD /accounts/addresses/"""

    serializer_class   = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def set_default(self, request, pk=None):
        address = self.get_object()
        address.is_default = True
        address.save()
        return Response(AddressSerializer(address).data)