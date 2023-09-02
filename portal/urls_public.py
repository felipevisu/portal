from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from .core.views import TenantView

urlpatterns = [
    path("", TenantView.as_view()),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)
