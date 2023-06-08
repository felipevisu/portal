from django.db import models, transaction
from django.db.models import F, Max


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
        return self.filter(is_published=True)

    def visible_to_user(self, user):
        if user.is_authenticated and user.is_staff:
            return self.all()
        return self.published()


class PublishableModel(models.Model):
    is_published = models.BooleanField(default=False)
    objects = models.Manager.from_queryset(PublishedQuerySet)()

    class Meta:
        abstract = True

    @property
    def is_visible(self):
        return self.is_published


class SortableModel(models.Model):
    sort_order = models.IntegerField(editable=False, db_index=True, null=True)

    class Meta:
        abstract = True

    def get_ordering_queryset(self):
        raise NotImplementedError("Unknown ordering queryset")

    def get_max_sort_order(self, qs):
        existing_max = qs.aggregate(Max("sort_order"))
        existing_max = existing_max.get("sort_order__max")
        return existing_max

    def save(self, *args, **kwargs):
        if self.pk is None:
            qs = self.get_ordering_queryset()
            existing_max = self.get_max_sort_order(qs)
            self.sort_order = 0 if existing_max is None else existing_max + 1
        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        if self.sort_order is not None:
            qs = self.get_ordering_queryset()
            qs.filter(sort_order__gt=self.sort_order).update(
                sort_order=F("sort_order") - 1
            )
        super().delete(*args, **kwargs)
