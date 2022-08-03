from django.core.exceptions import ValidationError
from django.forms import CharField, Field, MultipleChoiceField
from django_filters import Filter, MultipleChoiceFilter
from graphql_relay import from_global_id


def search_filter(queryset, name, value):
    return queryset.filter(name__search=value)


class GlobalIDFormField(Field):

    def clean(self, value):
        if not value and not self.required:
            return None

        try:
            _type, _id = from_global_id(value)
        except (TypeError, ValueError):
            raise ValidationError("Invalid ID specified.")

        try:
            CharField().clean(_id)
            CharField().clean(_type)
        except ValidationError:
            raise ValidationError("Invalid ID specified.")

        return value


class GlobalIDFilter(Filter):
    field_class = GlobalIDFormField

    def filter(self, qs, value):
        _id = None
        if value is not None:
            _, _id = from_global_id(value)
        return super(GlobalIDFilter, self).filter(qs, _id)


class GlobalIDMultipleChoiceField(MultipleChoiceField):
    def valid_value(self, value):
        GlobalIDFormField().clean(value)
        return True


class GlobalIDMultipleChoiceFilter(MultipleChoiceFilter):
    field_class = GlobalIDMultipleChoiceField

    def filter(self, qs, value):
        gids = [from_global_id(v)[1] for v in value]
        return super(GlobalIDMultipleChoiceFilter, self).filter(qs, gids)
