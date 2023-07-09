from typing import TYPE_CHECKING, Optional, Union
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.encoding import iri_to_uri
from django.utils.text import slugify
from text_unidecode import unidecode

if TYPE_CHECKING:
    from django.utils.safestring import SafeText


def build_absolute_uri(location: str, domain: Optional[str] = None) -> str:
    host = domain or Site.objects.get_current().domain
    protocol = "https" if settings.ENABLE_SSL else "http"  # type: ignore[misc] # circular import # noqa: E501
    current_uri = f"{protocol}://{host}"
    location = urljoin(current_uri, location)
    return iri_to_uri(location)


def generate_unique_slug(
    instance,
    slugable_value: str,
    slug_field_name: str = "slug",
    *,
    additional_search_lookup=None,
) -> str:
    slug = slugify(unidecode(slugable_value))

    ModelClass = instance.__class__

    search_field = f"{slug_field_name}__iregex"
    pattern = rf"{slug}-\d+$|{slug}$"
    lookup = {search_field: pattern}
    if additional_search_lookup:
        lookup.update(additional_search_lookup)

    slug_values = (
        ModelClass._default_manager.filter(**lookup)
        .exclude(pk=instance.pk)
        .values_list(slug_field_name, flat=True)
    )

    unique_slug = prepare_unique_slug(slug, slug_values)

    return unique_slug


def prepare_unique_slug(slug, slug_values):
    unique_slug: Union["SafeText", str] = slug
    extension = 1

    while unique_slug in slug_values:
        extension += 1
        unique_slug = f"{slug}-{extension}"

    return unique_slug
