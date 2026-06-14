import graphene
from branches.graphql.branch import schema as branch_schema


class Query(branch_schema.Query, graphene.ObjectType):
    pass


class Mutation(branch_schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
