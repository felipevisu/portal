from dataclasses import dataclass
from typing import Optional


@dataclass
class SendgridConfiguration:
    api_key: Optional[str]
    sender_name: Optional[str]
    sender_address: Optional[str]
    request_new_document_template_id: Optional[str]
    document_received_template_id: Optional[str]
    document_approved_template_id: Optional[str]
    document_declined_template_id: Optional[str]
