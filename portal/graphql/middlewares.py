from portal.graphql.investment.dataloaders import ItemsByInvestmentIdLoader
from portal.graphql.provider.dataloaders import (
    DocumentsByProviderIdLoader, ProvidersBySegmentIdLoader, SegmentByIdLoader)
from portal.graphql.vehicle.dataloaders import (
    CategoryByIdLoader, VehiclesByCategoryIdLoader)


class Loaders:
    def __init__(self):
        self.items_by_investment_loader = ItemsByInvestmentIdLoader()
        self.documents_by_provider_loader = DocumentsByProviderIdLoader()
        self.vehicles_by_category_loader = VehiclesByCategoryIdLoader()
        self.providers_by_segment_loader = ProvidersBySegmentIdLoader()
        self.category_loader = CategoryByIdLoader()
        self.segment_loader = SegmentByIdLoader()


class LoaderMiddleware:
    def resolve(self, next, root, info, **args):
        if not hasattr(info.context, 'loaders'):
            info.context.loaders = Loaders()

        return next(root, info, **args)
