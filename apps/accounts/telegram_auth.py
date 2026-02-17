import hashlib
import hmac
import time
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model

from .models import UserRole

MAX_AUTH_AGE_SECONDS = 86400


def _build_check_string(data: dict[str, Any]) -> str:
    parts = []
    for key in sorted(data.keys()):
        if key == "hash":
            continue
        value = data[key]
        if value is None:
            continue
        parts.append(f"{key}={value}")
    return "\n".join(parts)


def verify_telegram_payload(payload: dict[str, Any]) -> bool:
    token = settings.TELEGRAM_BOT_TOKEN
    incoming_hash = payload.get("hash")
    auth_date = payload.get("auth_date")

    if not token or not incoming_hash or not auth_date:
        return False

    try:
        auth_timestamp = int(auth_date)
    except (TypeError, ValueError):
        return False

    if int(time.time()) - auth_timestamp > MAX_AUTH_AGE_SECONDS:
        return False

    secret_key = hashlib.sha256(token.encode("utf-8")).digest()
    check_string = _build_check_string(payload)
    generated_hash = hmac.new(secret_key, check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    return hmac.compare_digest(generated_hash, incoming_hash)


def get_or_create_user_from_telegram(payload: dict[str, Any]):
    user_model = get_user_model()
    telegram_id = payload.get("id")
    if not telegram_id:
        raise ValueError("Telegram user id is required")

    telegram_id = int(telegram_id)
    username = f"tg_{telegram_id}"

    defaults = {
        "username": username,
        "first_name": payload.get("first_name", "")[:150],
        "last_name": payload.get("last_name", "")[:150],
        "telegram_username": (payload.get("username") or "")[:64],
        "telegram_photo_url": payload.get("photo_url") or "",
    }

    user, created = user_model.objects.update_or_create(telegram_id=telegram_id, defaults=defaults)

    if created:
        user.role = UserRole.PACKER
        user.set_unusable_password()
        user.save(update_fields=["role", "password"])

    return user
