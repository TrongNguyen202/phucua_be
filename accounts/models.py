# accounts/models.py — xoá UserProfile, chỉ giữ Address
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Address(models.Model):

    class AddressType(models.TextChoices):
        SHIPPING = "shipping", "Shipping"
        BILLING  = "billing",  "Billing"

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    full_name    = models.CharField(max_length=255)
    phone        = models.CharField(max_length=20)
    address      = models.TextField()
    city         = models.CharField(max_length=100)
    district     = models.CharField(max_length=100)
    ward         = models.CharField(max_length=100)
    postal_code  = models.CharField(max_length=20, blank=True)
    address_type = models.CharField(max_length=10, choices=AddressType.choices, default=AddressType.SHIPPING)
    is_default   = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user", "is_default"])]

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.address}, {self.ward}, {self.district}, {self.city}"