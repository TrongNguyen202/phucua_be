# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import register, login, csrf

urlpatterns = [
    path("register/",      register),
    path("login/",         login),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("csrf/", csrf),
    # ← thêm dòng này
]