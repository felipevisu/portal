from django.db import models

from portal.core.models import ModelWithDates, ModelWithSlug, PublishableModel
from portal.core.permissions import SessionPermissions


class Session(ModelWithDates, ModelWithSlug, PublishableModel):
    content = models.JSONField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField()

    class Meta:
        ordering = ['-created']
        permissions = (
            (SessionPermissions.MANAGE_SESSIONS.codename, "Manage sessions."),
        )
