import graphene

from users.graphql.auth import schema as auth_schema


class Query(graphene.ObjectType):
    test = graphene.String()  # TODO: Remove this


class Mutation(auth_schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
