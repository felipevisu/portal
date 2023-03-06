from dataclasses import dataclass
from typing import Optional


@dataclass
class SendgridConfiguration:
    api_key: Optional[str]
    sender_name: Optional[str]
    sender_address: Optional[str]
    request_new_document_from_provider_template_id: Optional[str]
    document_updated_confirmation_to_staff_template_id: Optional[str]
