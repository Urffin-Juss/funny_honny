import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.core.models import Client, Event, Order


@pytest.mark.django_db
def test_packer_sees_only_assigned_orders():
    user_model = get_user_model()
    owner = user_model.objects.create_user(username="owner", password="pass", role="owner")
    packer = user_model.objects.create_user(username="packer", password="pass", role="packer")

    client = Client.objects.create(full_name="Client", phone="+79990000000")
    event = Event.objects.create(name="Run", date="2026-03-10", city="Moscow")
    Order.objects.create(client=client, event=event)
    assigned = Order.objects.create(client=client, event=event, assigned_packer=packer)

    api = APIClient()
    api.force_authenticate(user=packer)
    response = api.get("/api/orders/")

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == assigned.id


@pytest.mark.django_db
def test_owner_can_open_dashboard():
    user_model = get_user_model()
    owner = user_model.objects.create_user(username="owner2", password="pass", role="owner")

    api = APIClient()
    api.force_authenticate(user=owner)

    response = api.get("/api/dashboard/")
    assert response.status_code == 200
    assert "orders_total" in response.data
