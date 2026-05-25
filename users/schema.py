import graphene

from users.graphql.auth import schema as auth_schema
from users.graphql.user import schema as user_schema


class Query(user_schema.Query, graphene.ObjectType):
    pass


class Mutation(auth_schema.Mutation, user_schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
