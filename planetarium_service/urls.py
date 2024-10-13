from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/", include("user.urls", namespace="user")),
    path(
        "api/planetarium-api/",
        include("planetarium_api.urls", namespace="planetarium_api"),
    ),
] + debug_toolbar_urls()
