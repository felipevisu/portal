import datetime

from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify


class ModelWithDates(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ModelWithSlug(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=256, unique=True)

    class Meta:
        abstract = True


class PublishedQuerySet(models.QuerySet):
    def published(self):
        today = datetime.date.today()
        return self.filter(
            Q(publication_date__lte=today) | Q(publication_date__isnull=True),
            is_published=True,
        )

    def visible_to_user(self, user):
        if user.is_authenticated and user.is_staff:
            return self.all()
        return self.published()


class PublishableModel(models.Model):
    publication_date = models.DateField(blank=True, null=True)
    is_published = models.BooleanField(default=False)

    objects = models.Manager.from_queryset(PublishedQuerySet)()

    class Meta:
        abstract = True

    @property
    def is_visible(self):
        return self.is_published and (
            self.publication_date is None
            or self.publication_date <= datetime.date.today()
        )
