from django.contrib.auth import get_user_model

from ..core.dataloaders import DataLoader

User = get_user_model()


class UserByIdLoader(DataLoader):
    context_key = "user_by_id"

    def batch_load(self, keys):
        user_map = User.objects.using(self.database_connection_name).in_bulk(keys)
        return [user_map.get(user_id) for user_id in keys]
