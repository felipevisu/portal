from collections import defaultdict

from ...investment.models import Item
from ..core.dataloaders import DataLoader


class ItemsByInvestmentIdLoader(DataLoader):
    context_key = "items_by_investment_id"

    def batch_load(self, keys):
        items_by_investments_ids = defaultdict(list)
        for item in Item.objects.filter(investment_id__in=keys).iterator():
            items_by_investments_ids[item.investment_id].append(item)
        return [items_by_investments_ids.get(key, []) for key in keys]
