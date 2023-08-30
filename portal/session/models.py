from django.db import models

from ..channel.models import Channel
from ..core.db.fields import SanitizedJSONField
from ..core.models import ModelWithDates, ModelWithSlug, PublishableModel
from ..core.permissions import SessionPermissions
from ..core.utils.editorjs import clean_editor_js


class Session(ModelWithDates, ModelWithSlug, PublishableModel):
    content = SanitizedJSONField(blank=True, null=True, sanitizer=clean_editor_js)
    date = models.DateTimeField()
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created"]
        permissions = (
            (SessionPermissions.MANAGE_SESSIONS.codename, "Manage sessions."),
        )
