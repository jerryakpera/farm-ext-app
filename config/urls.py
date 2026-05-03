"""
URL configuration for farm-ext project.
"""

# django_packages
from django.conf import settings
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.common.urls")),
    path("", include("core.farms.urls")),
    path("", include("core.profiles.urls")),
]

if settings.DEBUG:
    # If in development
    # django_packages
    from django.conf.urls.static import static

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    )

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
