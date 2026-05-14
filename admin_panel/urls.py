from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminDashboardView,
    AdminProductViewSet,
    AdminOrderViewSet,
    AdminUserView,
)

router = DefaultRouter()
router.register(r"products", AdminProductViewSet, basename="admin-product")
router.register(r"orders",   AdminOrderViewSet,   basename="admin-order")

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("users/",     AdminUserView.as_view(),      name="admin-users"),
    path("",           include(router.urls)),
]