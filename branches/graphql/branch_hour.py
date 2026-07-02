import graphene
from django.core.exceptions import ValidationError
from graphene_django import DjangoObjectType

from branches.models import BranchHour
from branches.services.branch_hour_service import BranchHourService
from utils.decorators import permission_required, staff_member_required
from utils.exceptions import ValidationGraphQLError
from utils.graphql import BaseConnection

DayOfWeekChoicesEnum = graphene.Enum.from_enum(BranchHour.DayOfWeekChoices)


class BranchHourNode(DjangoObjectType):
    id = graphene.ID(source="pk", required=True)

    class Meta:
        model = BranchHour
        exclude = ("branch",)
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        connection_class = BaseConnection


class BranchHourInput(graphene.InputObjectType):
    day_of_week = DayOfWeekChoicesEnum(required=True)
    from_hour = graphene.Time(required=True)
    to_hour = graphene.Time(required=True)


class SyncBranchHourInput(graphene.InputObjectType):
    branch_id = graphene.ID(required=True)
    hours = graphene.List(BranchHourInput, required=True)


class SyncBranchHour(graphene.Mutation):
    branch_hours = graphene.List(BranchHourNode)

    class Arguments:
        input = SyncBranchHourInput(required=True)

    @staff_member_required
    @permission_required(BranchHour, ["change"])
    def mutate(self, info, input: SyncBranchHourInput):
        # NOTE: If the user is not a branch operator,
        # use the branch_id from the input
        branch_id = info.context.user.branch_id or input.branch_id

        try:
            hours = BranchHourService.sync(branch_id, input.hours)
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return SyncBranchHour(branch_hours=hours)


class Query(graphene.ObjectType):
    pass


class Mutation(graphene.ObjectType):
    sync_branch_hour = SyncBranchHour.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
