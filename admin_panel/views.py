from django.shortcuts import render

# Create your views here.
from django.db.models import Sum, Count, Q, F, DecimalField, ExpressionWrapper
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets, status
from rest_framework.decorators import action

from products.models import Product
from products.serializers import ProductSerializer
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer
from variants.models import ProductVariant

User = get_user_model()

REVENUE_STATUSES = ["confirmed", "processing", "shipped", "delivered"]

subtotal_expr = ExpressionWrapper(
    F("unit_price") * F("quantity"),
    output_field=DecimalField()
)


# ── Dashboard ─────────────────────────────────────────────────────────────────

class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now     = timezone.now()
        today   = now.date()
        last_30 = now - timedelta(days=30)

        # Stats
        orders_total   = Order.objects.count()
        orders_today   = Order.objects.filter(created_at__date=today).count()
        orders_pending = Order.objects.filter(status="pending").count()
        orders_month   = Order.objects.filter(created_at__gte=last_30).count()

        revenue_month = OrderItem.objects.filter(
            order__created_at__gte=last_30,
            order__status__in=REVENUE_STATUSES
        ).aggregate(total=Sum(subtotal_expr))["total"] or 0
        revenue_total = OrderItem.objects.filter(
            order__status__in=REVENUE_STATUSES
        ).aggregate(total=Sum(subtotal_expr))["total"] or 0
        products_total  = Product.objects.count()
        products_active = Product.objects.filter(is_active=True).count()
        low_stock       = ProductVariant.objects.filter(stock__lte=5, is_active=True).count()

        users_total = User.objects.filter(is_staff=False).count()
        users_month = User.objects.filter(date_joined__gte=last_30, is_staff=False).count()

        # Revenue chart — 7 ngày gần nhất
        revenue_chart = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            rev = OrderItem.objects.filter(
                order__created_at__date=day,
                order__status__in=REVENUE_STATUSES
            ).aggregate(total=Sum(subtotal_expr))["total"] or 0

            revenue_chart.append({
                "date":    day.strftime("%d/%m"),
                "revenue": float(rev),
                "orders":  Order.objects.filter(created_at__date=day).count(),
            })

        # Recent orders
        recent = Order.objects.select_related("user").prefetch_related(
            "items"
        ).order_by("-created_at")[:8]

        # Top sản phẩm bán chạy
        top_products = (
            OrderItem.objects
            .values("variant__product__name", "variant__product__id")
            .annotate(total_sold=Sum("quantity"))
            .order_by("-total_sold")[:5]
        )

        # Breakdown theo status
        status_breakdown = list(
            Order.objects.values("status").annotate(count=Count("id"))
        )

        return Response({
            "stats": {
                "orders":   { "total": orders_total, "today": orders_today, "pending": orders_pending, "month": orders_month },
                "revenue":  { "month": float(revenue_month),"total": float(revenue_total), },
                "products": { "total": products_total, "active": products_active, "low_stock": low_stock },
                "users":    { "total": users_total, "month": users_month },
            },
            "revenue_chart":    revenue_chart,
            "status_breakdown": status_breakdown,
            "recent_orders": [
                {
                    "id":          o.id,
                    "user":        o.user.username if o.user else "Guest",
                    "status":      o.status,
                    "total":       float(o.total),
                    "created_at":  o.created_at.strftime("%d/%m/%Y %H:%M"),
                    "items_count": o.items.count(),
                }
                for o in recent
            ],
            "top_products": [
                {
                    "name":       t["variant__product__name"],
                    "id":         t["variant__product__id"],
                    "total_sold": t["total_sold"],
                }
                for t in top_products
            ],
        })


# ── Products ──────────────────────────────────────────────────────────────────

class AdminProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class   = ProductSerializer
    lookup_field       = "id"

    def get_queryset(self):
        qs = Product.objects.select_related("category").prefetch_related(
            "images", "variants"
        ).order_by("-created_at")

        search   = self.request.query_params.get("search")
        category = self.request.query_params.get("category")
        active   = self.request.query_params.get("status")

        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if category:
            qs = qs.filter(category_id=category)
        if active == "active":
            qs = qs.filter(is_active=True)
        elif active == "inactive":
            qs = qs.filter(is_active=False)

        return qs

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, id=None):
        product = self.get_object()
        product.is_active = not product.is_active
        product.save()
        return Response({"is_active": product.is_active})

    @action(detail=True, methods=["post"])
    def toggle_featured(self, request, id=None):
        product = self.get_object()
        product.is_featured = not product.is_featured
        product.save()
        return Response({"is_featured": product.is_featured})


# ── Orders ────────────────────────────────────────────────────────────────────

class AdminOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class   = OrderSerializer
    http_method_names  = ["get", "patch", "head", "options"]

    def get_queryset(self):
        qs = Order.objects.select_related("user").prefetch_related(
            "items__variant__product",
            "items__variant__size",
            "items__variant__color",
        ).order_by("-created_at")

        order_status = self.request.query_params.get("status")
        search       = self.request.query_params.get("search")

        if order_status:
            qs = qs.filter(status=order_status)
        if search:
            qs = qs.filter(
                Q(id__icontains=search) |
                Q(shipping_full_name__icontains=search) |
                Q(shipping_phone__icontains=search) |
                Q(user__username__icontains=search)
            )

        return qs

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        order      = self.get_object()
        new_status = request.data.get("status")
        valid      = [s[0] for s in Order.Status.choices]

        if new_status not in valid:
            return Response(
                {"detail": f"Trạng thái không hợp lệ. Chọn: {valid}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)


# ── Users ─────────────────────────────────────────────────────────────────────

class AdminUserView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.query_params.get("search", "")
        page   = int(request.query_params.get("page", 1))
        size   = 20

        qs = User.objects.filter(is_staff=False).order_by("-date_joined")
        if search:
            qs = qs.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )

        total = qs.count()
        users = qs[(page - 1) * size: page * size]

        return Response({
            "count":   total,
            "results": [
                {
                    "id":           u.id,
                    "username":     u.username,
                    "email":        u.email,
                    "full_name":    f"{u.last_name} {u.first_name}".strip(),
                    "is_active":    u.is_active,
                    "date_joined":  u.date_joined.strftime("%d/%m/%Y"),
                    "orders_count": Order.objects.filter(user=u).count(),
                }
                for u in users
            ],
        })

    def patch(self, request):
        user_id   = request.data.get("id")
        is_active = request.data.get("is_active")

        try:
            u = User.objects.get(id=user_id, is_staff=False)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        u.is_active = is_active
        u.save()
        return Response({"id": u.id, "is_active": u.is_active})

# Thêm vào admin_panel/views.py

import requests
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework import status


class UploadImageView(APIView):
    """
    POST /api/admin-panel/upload-image/
    Upload ảnh lên Imagur, trả về URL.
    """
    permission_classes = [IsAdminUser]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        image_file = request.FILES.get("image")
        if not image_file:
            return Response({"error": "Không có file ảnh."}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://imagur.org/wp-admin/admin-ajax.php"
        payload = {"action": "imagur_upload"}
        files = {
            "image": (
                image_file.name,
                image_file,
                image_file.content_type,
            )
        }
        headers = {
            "accept": "*/*",
            "origin": "https://imagur.org",
            "referer": "https://imagur.org/",
            "user-agent": "Mozilla/5.0",
        }

        try:
            resp = requests.post(url, headers=headers, data=payload, files=files, timeout=30)
            data = resp.json()
        except Exception as e:
            return Response({"error": f"Upload thất bại: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

        if not data.get("success"):
            return Response({"error": "Upload ảnh thất bại."}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({"url": data["data"]["direct_url"]}, status=status.HTTP_200_OK)