from django.db.models import Count, Sum
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import UserRole

from .models import Client, Event, Order, Product, Stock, Task
from .permissions import IsOwnerOrAdmin, IsOwnerOrAdminWriteElseRead
from .serializers import (
    ClientSerializer,
    EventSerializer,
    OrderSerializer,
    ProductSerializer,
    StockSerializer,
    TaskSerializer,
)


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerOrAdminWriteElseRead]


class EventViewSet(BaseModelViewSet):
    queryset = Event.objects.all().order_by("-date")
    serializer_class = EventSerializer
    search_fields = ["name", "city"]
    permission_classes = [IsOwnerOrAdmin]


class ClientViewSet(BaseModelViewSet):
    queryset = Client.objects.all().order_by("full_name")
    serializer_class = ClientSerializer
    search_fields = ["full_name", "phone", "city", "pets"]
    permission_classes = [IsOwnerOrAdmin]


class ProductViewSet(BaseModelViewSet):
    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer
    filterset_fields = ["product_type", "size"]
    permission_classes = [IsOwnerOrAdmin]


class StockViewSet(BaseModelViewSet):
    queryset = Stock.objects.select_related("product").all().order_by("location")
    serializer_class = StockSerializer
    filterset_fields = ["location", "product"]
    permission_classes = [IsOwnerOrAdmin]


class OrderViewSet(BaseModelViewSet):
    queryset = Order.objects.select_related("client", "event", "assigned_packer").prefetch_related("items").all()
    serializer_class = OrderSerializer
    filterset_fields = ["status", "event", "assigned_packer"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == UserRole.PACKER:
            return qs.filter(assigned_packer=user)
        return qs


class TaskViewSet(BaseModelViewSet):
    queryset = Task.objects.select_related("assignee", "event", "order").all().order_by("-created_at")
    serializer_class = TaskSerializer
    filterset_fields = ["status", "task_type", "assignee"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role == UserRole.PACKER:
            return qs.filter(assignee=user)
        return qs


class DashboardSummaryView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role != UserRole.OWNER:
            return Response({"detail": "Only owner can access dashboard"}, status=403)

        data = {
            "orders_total": Order.objects.count(),
            "orders_by_status": list(Order.objects.values("status").annotate(total=Count("id"))),
            "tasks_open": Task.objects.exclude(status="done").count(),
            "stock_units_total": Stock.objects.aggregate(total=Sum("quantity")).get("total") or 0,
        }
        return Response(data)
