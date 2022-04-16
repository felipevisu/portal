from django_filters import FilterSet

from ...provider.models import Document, Provider, Segment


class DocumentFilter(FilterSet):
    class Meta:
        model = Document
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'is_published': ['exact'],
            'expires': ['exact'],
            'begin_date': ['lte', 'gte', 'exact'],
            'expiration_date': ['lte', 'gte', 'exact']
        }


class ProviderFilter(FilterSet):
    class Meta:
        model = Provider
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'document_number': ['exact'],
            'is_published': ['exact'],
        }


class SegmentFilter(FilterSet):
    class Meta:
        model = Segment
        fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }
