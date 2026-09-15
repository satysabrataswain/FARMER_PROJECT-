from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "api/auth/",
        include("accounts.urls"),
    ),

    path(
        "api/farmers/",
        include("farmers.urls"),
    ),

    path(
        "api/sellers/",
        include("sellers.urls"),
    ),

    path(
        "api/products/",
        include("products.urls"),
    ),

    path(
        "api/cart/",
        include("cart.urls"),
    ),

    path(
        "api/orders/",
        include("orders.urls"),
    ),

    path(
        "api/delivery/",
        include("delivery.urls"),
    ),
    path(
    "api/returns/",
    include("returns.urls"),
  ),
    path(
    "api/notifications/",
    include("notifications.urls")
  ),
    path(
    "api/complaints/",
    include("complaints.urls"),
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )