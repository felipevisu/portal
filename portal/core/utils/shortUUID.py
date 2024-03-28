import base64
import uuid


def generate_short_uuid():
    unique_id = uuid.uuid4()
    uuid_bytes = unique_id.bytes
    encoded_uuid = base64.urlsafe_b64encode(uuid_bytes)
    short_uuid = encoded_uuid.decode("utf-8").rstrip("=")

    return short_uuid
