from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, SePayWebhookView

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")

urlpatterns = router.urls + [
    path("payments/sepay-webhook/", SePayWebhookView.as_view(), name="sepay-webhook"),
]