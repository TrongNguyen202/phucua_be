from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import register, login, change_password  # ← thêm import

urlpatterns = [
    path("register/",        register),
    path("login/",           login),
    path("token/refresh/",   TokenRefreshView.as_view()),
    path("change-password/", change_password),  # ← thêm dòng này
]