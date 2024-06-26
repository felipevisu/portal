import graphene

from .account.schema import Mutation as AccountMutation
from .account.schema import Query as AccountQuery
from .attribute.schema import Mutation as AttributeMutation
from .attribute.schema import Query as AttributeQuery
from .channel.schema import Mutation as ChannelMutation
from .channel.schema import Query as ChannelQuery
from .document.schema import Mutation as DocumentMutation
from .document.schema import Query as DocumentQuery
from .entry.schema import Mutation as EntryMutation
from .entry.schema import Query as EntryQuery
from .event.schema import Query as EventQuery
from .investment.schema import Mutation as InvestmentMutation
from .investment.schema import Query as InvestmentQuery
from .plugins.schema import Mutation as PluginsMutation
from .plugins.schema import Query as PluginsQuery
from .session.schema import Mutation as SessionMutation
from .session.schema import Query as SessionQuery


class Query(
    AccountQuery,
    AttributeQuery,
    ChannelQuery,
    DocumentQuery,
    EntryQuery,
    EventQuery,
    InvestmentQuery,
    PluginsQuery,
    SessionQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    AccountMutation,
    AttributeMutation,
    ChannelMutation,
    DocumentMutation,
    EntryMutation,
    InvestmentMutation,
    PluginsMutation,
    SessionMutation,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
