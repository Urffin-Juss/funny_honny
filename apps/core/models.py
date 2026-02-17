from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Event(TimeStampedModel):
    name = models.CharField(max_length=255)
    date = models.DateField()
    city = models.CharField(max_length=120)
    distances = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.date})"


class Client(TimeStampedModel):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=255, blank=True)
    social_links = models.TextField(blank=True)
    pets = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.full_name} ({self.phone})"


class ProductType(models.TextChoices):
    MEDAL = "medal", "Medal"
    SOCKS = "socks", "Socks"
    SLOT = "slot", "Slot"
    OTHER = "other", "Other"


class Product(TimeStampedModel):
    product_type = models.CharField(max_length=20, choices=ProductType.choices)
    name = models.CharField(max_length=255)
    variant = models.CharField(max_length=120, blank=True)
    size = models.CharField(max_length=30, blank=True)

    class Meta:
        unique_together = ("product_type", "name", "variant", "size")

    def __str__(self) -> str:
        return f"{self.name} {self.variant}".strip()


class StockLocation(models.TextChoices):
    LOCATION_1 = "location_1", "Location 1"
    LOCATION_2 = "location_2", "Location 2"
    LOCATION_3 = "location_3", "Location 3"


class Stock(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks")
    location = models.CharField(max_length=30, choices=StockLocation.choices)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("product", "location")

    def __str__(self) -> str:
        return f"{self.product} @ {self.location}: {self.quantity}"


class OrderStatus(models.TextChoices):
    NEW = "new", "New"
    ASSEMBLING = "assembling", "Assembling"
    READY = "ready", "Ready"
    SHIPPED = "shipped", "Shipped"
    COMPLETED = "completed", "Completed"
    CANCELED = "canceled", "Canceled"


class Order(TimeStampedModel):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="orders")
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name="orders")
    assigned_packer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="packed_orders",
    )
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.NEW)
    comment = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Order #{self.pk} - {self.client.full_name}"


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.product} x{self.quantity}"


class TaskType(models.TextChoices):
    EVENT = "event", "Event"
    ORDER = "order", "Order"


class TaskStatus(models.TextChoices):
    TODO = "todo", "Ожидает"
    IN_PROGRESS = "in_progress", "В работе"
    DONE = "done", "Сделано"


class Task(TimeStampedModel):
    task_type = models.CharField(max_length=20, choices=TaskType.choices)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tasks")
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO)
    description = models.TextField()

    def __str__(self) -> str:
        return f"Task #{self.pk} ({self.status})"
