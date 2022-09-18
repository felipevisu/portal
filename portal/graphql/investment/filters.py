
import django_filters

from ...investment.models import Investment
from ..core.types import FilterInputObjectType


class InvestmentFilter(django_filters.FilterSet):

    class Meta:
        model = Investment
        fields = ['year', 'month', 'is_published']


class InvestmentFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = InvestmentFilter
