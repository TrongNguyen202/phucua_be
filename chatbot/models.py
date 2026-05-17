from django.db import models
from users.models import User
# Create your models here.
class AIConversation(models.Model):

    user = models.ForeignKey(User)

    role = models.CharField(max_length=20)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)



class UserAIMemory(models.Model):

    user = models.OneToOneField(User)

    favorite_style = models.CharField(max_length=255, blank=True)

    favorite_colors = models.JSONField(default=list)

    favorite_categories = models.JSONField(default=list)

    budget_min = models.IntegerField(null=True)

    budget_max = models.IntegerField(null=True)

    sizes = models.JSONField(default=list)

    updated_at = models.DateTimeField(auto_now=True)