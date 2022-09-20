import graphene

from .account.schema import Mutation as AccountMutation, Query as AccountQuery
from .document.schema import Mutation as DocumentMutation, Query as DocumentQuery
from .investment.schema import Mutation as InvestmentMutation, Query as InvestmentQuery
from .provider.schema import Mutation as ProviderMutation, Query as ProviderQuery
from .session.schema import Mutation as MutationQuery, Query as SessionQuery
from .vehicle.schema import Mutation as VehicleMutation, Query as VehicleQuery


class Query(
    AccountQuery,
    DocumentQuery,
    InvestmentQuery,
    ProviderQuery,
    SessionQuery,
    VehicleQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    AccountMutation,
    DocumentMutation,
    VehicleMutation,
    ProviderMutation,
    InvestmentMutation,
    MutationQuery,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
