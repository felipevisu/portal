from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

from portal.core.views import TenantView

from .graphql.schema import schema
from .graphql.views import GraphQLView

urlpatterns = [
    path("", TenantView.as_view()),
    path("admin/", admin.site.urls),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema)), name="api"),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
    urlpatterns += static("/media/", document_root=settings.MEDIA_ROOT)
