import graphene

from users.schema import schema as users_schema


class Query(users_schema.Query, graphene.ObjectType):
    pass


class Mutation(users_schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
