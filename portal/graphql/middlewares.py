from portal.graphql.investment.dataloaders import ItemsByInvestmentIdLoader
from portal.graphql.provider.dataloaders import DocumentsByProviderIdLoader


class Loaders:
    def __init__(self):
        self.items_by_investment_loader = ItemsByInvestmentIdLoader()
        self.documents_by_provider_loader = DocumentsByProviderIdLoader()


class LoaderMiddleware:
    def resolve(self, next, root, info, **args):
        if not hasattr(info.context, 'loaders'):
            info.context.loaders = Loaders()

        return next(root, info, **args)
