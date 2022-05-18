def search_filter(queryset, name, value):
    return queryset.filter(name__search=value)
