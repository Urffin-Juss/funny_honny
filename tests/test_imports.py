from io import BytesIO

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from openpyxl import Workbook
from rest_framework.test import APIClient

from apps.core.models import Client
from apps.imports.models import ImportBatch, ImportBatchStatus


def make_xlsx_bytes(rows):
    wb = Workbook()
    ws = wb.active
    ws.append(["phone", "full_name", "city"])
    for row in rows:
        ws.append(row)
    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


@pytest.mark.django_db
def test_import_batch_creates_clients_and_raw_rows(monkeypatch):
    user_model = get_user_model()
    owner = user_model.objects.create_user(username="owner_import", password="pass", role="owner")

    from apps.imports import views as import_views

    monkeypatch.setattr(import_views.process_import_batch, "delay", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("no broker")))

    excel = make_xlsx_bytes([
        ["+70000000001", "Runner One", "Moscow"],
        ["+70000000002", "Runner Two", "Kazan"],
    ])
    upload = SimpleUploadedFile(
        "participants.xlsx",
        excel,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    api = APIClient()
    api.force_authenticate(user=owner)
    response = api.post("/api/imports/", data={"source_file": upload}, format="multipart")

    assert response.status_code == 201

    batch = ImportBatch.objects.get(id=response.data["id"])
    assert batch.status == ImportBatchStatus.DONE
    assert batch.rows.count() == 2
    assert Client.objects.filter(phone="+70000000001", full_name="Runner One").exists()
    assert Client.objects.filter(phone="+70000000002", full_name="Runner Two").exists()


@pytest.mark.django_db
def test_import_batch_rejects_missing_columns(monkeypatch):
    user_model = get_user_model()
    owner = user_model.objects.create_user(username="owner_import2", password="pass", role="owner")

    from apps.imports import views as import_views

    monkeypatch.setattr(import_views.process_import_batch, "delay", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("no broker")))

    wb = Workbook()
    ws = wb.active
    ws.append(["name", "email"])
    ws.append(["Name", "a@example.com"])
    stream = BytesIO()
    wb.save(stream)

    upload = SimpleUploadedFile(
        "bad.xlsx",
        stream.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    api = APIClient()
    api.force_authenticate(user=owner)
    response = api.post("/api/imports/", data={"source_file": upload}, format="multipart")

    assert response.status_code == 201
    batch = ImportBatch.objects.get(id=response.data["id"])
    assert batch.status == ImportBatchStatus.FAILED
    assert "Missing required columns" in batch.error_message
