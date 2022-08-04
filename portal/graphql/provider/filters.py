from datetime import timedelta

import django_filters
from django.db.models import Q
from django.utils import timezone

from ...provider.models import Document, Provider, Segment
from ..core.filters import GlobalIDMultipleChoiceFilter, search_filter
from ..utils import resolve_global_ids_to_primary_keys
from . import types as provider_types


def filter_by_documents_close_to_expire(qs, _, value):
    if value:
        today = timezone.now()
        week_ahead = timezone.now() + timedelta(days=7)
        documents = Document.objects.filter(expires=True, expiration_date__range=[today, week_ahead])
        qs = qs.filter(id__in=documents.values_list('provider_id'))

    return qs


def filter_by_expired_documents(qs, _, value):
    if value:
        documents = Document.objects.filter(expires=True, expiration_date__lte=timezone.now())
        qs = qs.filter(id__in=documents.values_list('provider_id'))

    return qs


def filter_segments(qs, _, value):
    if value:
        _, segment_pks = resolve_global_ids_to_primary_keys(
            value, provider_types.Segment
        )
        return qs.filter(segment_id__in=segment_pks)
    return qs


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
    segments = GlobalIDMultipleChoiceFilter(method=filter_segments)
    expired = django_filters.BooleanFilter(method=filter_by_expired_documents)
    close_to_expire = django_filters.BooleanFilter(method=filter_by_documents_close_to_expire)

    class Meta:
        model = Provider
        fields = ['is_published', 'segment']


class SegmentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=search_filter)

    class Meta:
        model = Segment
        fields = ['search']
