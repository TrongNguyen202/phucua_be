from django.db import models
from django.utils.text import slugify


class Category(models.Model):

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    description = models.TextField(blank=True)

    image = models.URLField(blank=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["name", "is_active"]),
        ]

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name