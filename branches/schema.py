import graphene

from branches.graphql.branch import schema as branch_schema
from branches.graphql.branch_hour import schema as branch_hour_schema


class Query(branch_schema.Query, branch_hour_schema.Query, graphene.ObjectType):
    pass


class Mutation(
    branch_schema.Mutation, branch_hour_schema.Mutation, graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
