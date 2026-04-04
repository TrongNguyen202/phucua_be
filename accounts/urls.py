# accounts/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeView, AddressViewSet

router = DefaultRouter()
router.register(r"addresses", AddressViewSet, basename="address")

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),  # ← thêm dòng này
    path("", include(router.urls)),
]