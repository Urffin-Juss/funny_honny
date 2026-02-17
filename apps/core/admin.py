from django.contrib import admin

from .models import Client, Event, Order, OrderItem, Product, Stock, Task


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "city")
    search_fields = ("name", "city")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "city", "pets")
    search_fields = ("full_name", "phone", "pets")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_type", "name", "variant", "size")
    list_filter = ("product_type", "size")


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("product", "location", "quantity")
    list_filter = ("location",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "event", "status", "assigned_packer")
    list_filter = ("status", "event")
    inlines = [OrderItemInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "task_type", "assignee", "status", "created_at")
    list_filter = ("status", "task_type")
