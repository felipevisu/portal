import django_filters

from ...provider.models import Document, Provider, Segment
from ..core.filters import search_filter


class DocumentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)

    class Meta:
        model = Document
        fields = {
            'is_published': ['exact'],
            'expires': ['exact'],
            'begin_date': ['lte', 'gte', 'exact'],
            'expiration_date': ['lte', 'gte', 'exact']
        }


class ProviderFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)

    class Meta:
        model = Provider
        fields = ['is_published', 'segment']


class SegmentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)

    class Meta:
        model = Segment
        fields = ['search']
