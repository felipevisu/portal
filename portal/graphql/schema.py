import graphene

from .account.schema import Mutation as AccountMutation, Query as AccountQuery
from .document.schema import Mutation as DocumentMutation, Query as DocumentQuery
from .entry.schema import Mutation as EntryMutation, Query as EntryQuery
from .investment.schema import Mutation as InvestmentMutation, Query as InvestmentQuery
from .session.schema import Mutation as MutationQuery, Query as SessionQuery


class Query(
    AccountQuery,
    DocumentQuery,
    InvestmentQuery,
    SessionQuery,
    EntryQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    AccountMutation,
    DocumentMutation,
    EntryMutation,
    InvestmentMutation,
    MutationQuery,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
