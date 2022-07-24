from portal.graphql.investment.dataloaders import ItemsByInvestmentIdLoader


class Loaders:
    def __init__(self):
        self.items_by_investment_loader = ItemsByInvestmentIdLoader()


class LoaderMiddleware:
    def resolve(self, next, root, info, **args):
        if not hasattr(info.context, 'loaders'):
            info.context.loaders = Loaders()

        return next(root, info, **args)
