import graphene
from django.core.exceptions import ValidationError
from graphene_django import DjangoObjectType

from branches.graphql.branch_hour import BranchHourNode
from branches.models import Branch
from branches.services.branch_service import BranchService
from utils.decorators import permission_required, staff_member_required
from utils.exceptions import ValidationGraphQLError
from utils.graphql import BaseConnection, ConnectionField


class BranchNode(DjangoObjectType):
    id = graphene.ID(source="pk", required=True)
    branch_hours = graphene.List(BranchHourNode)

    class Meta:
        model = Branch
        exclude = ("created_at", "updated_at")
        filter_fields = ["is_active"]
        interfaces = (graphene.relay.Node,)
        connection_class = BaseConnection

    def resolve_branch_hours(self, info, **kwargs):
        return self.branch_hours.all()


class CreateBranchInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    address = graphene.String()
    is_active = graphene.Boolean(default_value=True)


class CreateBranch(graphene.Mutation):
    branch = graphene.Field(BranchNode)

    class Arguments:
        input = CreateBranchInput(required=True)

    @staff_member_required
    @permission_required(Branch, ["add"])
    def mutate(self, info, input: CreateBranchInput):
        try:
            branch = BranchService.create_branch(
                name=input.name,
                address=input.address,
                is_active=input.is_active,
            )
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return CreateBranch(branch=branch)


class Query(graphene.ObjectType):
    all_branches = ConnectionField(BranchNode)

    @staff_member_required
    @permission_required(Branch, ["view"])
    def resolve_all_branches(self, info, **kwargs):
        return Branch.objects.all()


class Mutation(graphene.ObjectType):
    create_branch = CreateBranch.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
