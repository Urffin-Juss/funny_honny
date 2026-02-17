import hashlib
import hmac
import time

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.telegram_auth import verify_telegram_payload


def build_payload(token: str) -> dict:
    payload = {
        "id": 123456,
        "first_name": "Rick",
        "last_name": "Runner",
        "username": "rickrun",
        "photo_url": "https://example.com/photo.jpg",
        "auth_date": int(time.time()),
    }
    data_check_string = "\n".join([f"{k}={payload[k]}" for k in sorted(payload.keys())])
    secret = hashlib.sha256(token.encode("utf-8")).digest()
    payload["hash"] = hmac.new(secret, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()
    return payload


@pytest.mark.django_db
def test_verify_telegram_payload_valid(settings):
    token = "bot-token-123"
    settings.TELEGRAM_BOT_TOKEN = token
    payload = build_payload(token)

    assert verify_telegram_payload(payload) is True


@pytest.mark.django_db
def test_telegram_auth_endpoint_creates_user(client, settings):
    token = "bot-token-123"
    settings.TELEGRAM_BOT_TOKEN = token
    settings.TELEGRAM_BOT_USERNAME = "my_test_bot"

    payload = build_payload(token)
    response = client.post(
        "/auth/telegram/",
        data=payload,
        content_type="application/json",
    )

    assert response.status_code == 200

    user_model = get_user_model()
    user = user_model.objects.get(telegram_id=payload["id"])
    assert user.username == f"tg_{payload['id']}"
    assert client.session.get("_auth_user_id") is not None
