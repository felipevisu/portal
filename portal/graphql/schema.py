import graphene

from .account.schema import Mutation as AccountMutation
from .account.schema import Query as AccountQuery
from .investment.schema import Mutation as InvestmentMutation
from .investment.schema import Query as InvestmentQuery
from .provider.schema import Mutation as ProviderMutation
from .provider.schema import Query as ProviderQuery
from .session.schema import Mutation as MutationQuery
from .session.schema import Query as SessionQuery
from .vehicle.schema import Mutation as VehicleMutation
from .vehicle.schema import Query as VehicleQuery


class Query(
    AccountQuery,
    InvestmentQuery,
    ProviderQuery,
    SessionQuery,
    VehicleQuery,
    graphene.ObjectType
):
    pass


class Mutation(
    AccountMutation,
    VehicleMutation,
    ProviderMutation,
    InvestmentMutation,
    MutationQuery
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
