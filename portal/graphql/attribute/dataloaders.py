from ...attribute.models import Attribute, AttributeValue
from ..core.dataloaders import DataLoader


class AttributesByAttributeId(DataLoader):
    context_key = "attributes_by_id"

    def batch_load(self, keys):
        attributes = Attribute.objects.using(self.database_connection_name).in_bulk(
            keys
        )
        return [attributes.get(key) for key in keys]
