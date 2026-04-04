from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt  # 👈 THÊM
from django.http import JsonResponse


@ensure_csrf_cookie
def csrf(request):
    return JsonResponse({"message": "ok"})


# 🔥 BYPASS CSRF
@csrf_exempt
@api_view(["POST"])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔥 BYPASS CSRF
@csrf_exempt
@api_view(["POST"])
def login(request):

    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })

    return Response(
        {"error": "Invalid username or password"},
        status=status.HTTP_401_UNAUTHORIZED
    )