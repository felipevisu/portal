from graphene_django.views import GraphQLView as BaseGraphQLView
from graphene_file_upload.django import FileUploadGraphQLView


class GraphQLView(FileUploadGraphQLView, BaseGraphQLView):
    graphiql_template = "graphql/playground.html"

    def __init__(
        self,
        schema=None,
        executor=None,
        middleware=None,
        root_value=None,
        graphiql=True,
        pretty=False,
        batch=False,
        backend=None,
        subscription_path=None,
    ):
        super().__init__(
            schema,
            executor,
            middleware,
            root_value,
            graphiql,
            pretty,
            batch,
            backend,
            subscription_path,
        )
