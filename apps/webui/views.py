from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from apps.core.models import Notification


@require_GET
def landing_view(request):
    return render(request, "webui/landing.html", {"shop_url": settings.SHOP_URL})


@require_GET
def shop_redirect_view(request):
    return redirect(settings.SHOP_URL)


class RWLLoginView(LoginView):
    template_name = "webui/login.html"
    redirect_authenticated_user = True


@require_POST
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def workspace_view(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by("-created_at")[:8]
    return render(
        request,
        "webui/workspace.html",
        {
            "shop_url": settings.SHOP_URL,
            "notifications": notifications,
        },
    )
