import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from django.http import HttpRequest

from ...account.models import User

if TYPE_CHECKING:
    from .dataloaders import DataLoader


class PortalContext(HttpRequest):
    _cached_user: Optional[User]
    decoded_auth_token: Optional[Dict[str, Any]]
    allow_replica: bool = True
    dataloaders: Dict[str, "DataLoader"]
    user: Optional[User]  # type: ignore[assignment]
    request_time: datetime.datetime
