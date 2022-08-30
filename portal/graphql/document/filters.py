
import django_filters

from ...document.models import Document
from ..core.filters import search_filter


def filter_owner(queryset, name, value):
    print('aqui')
    if value == 'vehicle':
        return queryset.filter(provider=None)
    if value == 'provider':
        return queryset.filter(vehicle=None)
    return queryset


OWNER_CHOICES = (
    ('provider', 'Provider'),
    ('vehicle', 'Vehicle'),
)


class DocumentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)
    owner = django_filters.ChoiceFilter(choices=OWNER_CHOICES, method=filter_owner)

    class Meta:
        model = Document
        fields = {
            'is_published': ['exact'],
            'expires': ['exact'],
            'begin_date': ['lte', 'gte', 'exact'],
            'expiration_date': ['lte', 'gte', 'exact']
        }
