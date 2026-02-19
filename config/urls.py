from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from apps.core.views import (
    ClientViewSet,
    DashboardSummaryView,
    EventViewSet,
    OrderViewSet,
    ProductViewSet,
    StockViewSet,
    TaskViewSet,
)
from apps.imports.views import ImportBatchViewSet
from apps.webui.views import (
    RWLLoginView,
    landing_view,
    logout_view,
    shop_redirect_view,
    workspace_view,
)

router = DefaultRouter()
router.register("events", EventViewSet, basename="event")
router.register("clients", ClientViewSet, basename="client")
router.register("products", ProductViewSet, basename="product")
router.register("orders", OrderViewSet, basename="order")
router.register("stocks", StockViewSet, basename="stock")
router.register("tasks", TaskViewSet, basename="task")
router.register("imports", ImportBatchViewSet, basename="import")

urlpatterns = [
    path("", landing_view, name="landing"),
    path("shop/", shop_redirect_view, name="shop"),
    path("login/", RWLLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("workspace/", workspace_view, name="workspace"),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/dashboard/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
