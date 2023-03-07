from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.timezone import now

from ..document.models import Document
from ..entry.models import Entry
from . import EventTypes


class Event(models.Model):
    date = models.DateTimeField(default=now, editable=False)
    type = models.CharField(
        max_length=255,
        choices=[(type_name.upper(), type_name) for type_name, _ in EventTypes.CHOICES],
    )
    parameters = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    document = models.ForeignKey(
        Document,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="events",
    )

    class Meta:
        ordering = ("date",)

    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.type!r}, user={self.user!r})"