import django_filters

from ...session.models import Session
from ..core.filters import search_filter
from ..core.types import FilterInputObjectType


class SessionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)

    class Meta:
        model = Session
        fields = ["search", "is_published", "channel"]


class SessionFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = SessionFilter
