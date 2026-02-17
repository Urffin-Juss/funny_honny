import json

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from apps.accounts.telegram_auth import get_or_create_user_from_telegram, verify_telegram_payload


@require_GET
def landing_view(request):
    return render(request, "webui/landing.html", {"shop_url": settings.SHOP_URL})


@require_GET
def shop_redirect_view(request):
    return redirect(settings.SHOP_URL)


@require_GET
@ensure_csrf_cookie
def login_view(request):
    return render(
        request,
        "webui/login.html",
        {
            "telegram_bot_username": settings.TELEGRAM_BOT_USERNAME,
            "next_url": request.GET.get("next", "/workspace/"),
        },
    )


@require_POST
def telegram_auth_view(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    if not verify_telegram_payload(payload):
        return JsonResponse({"detail": "Telegram verification failed"}, status=400)

    user = get_or_create_user_from_telegram(payload)
    login(request, user)
    return JsonResponse({"detail": "ok"})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def workspace_view(request):
    return render(request, "webui/workspace.html", {"shop_url": settings.SHOP_URL})
