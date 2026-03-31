from rest_framework.routers import DefaultRouter
from .views import SizeViewSet, ColorViewSet, ProductVariantViewSet

router = DefaultRouter()
router.register(r"sizes",    SizeViewSet,           basename="size")
router.register(r"colors",   ColorViewSet,          basename="color")
router.register(r"variants", ProductVariantViewSet, basename="variant")

urlpatterns = router.urls