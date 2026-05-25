import graphene
from django.core.exceptions import ValidationError
from graphene_django import DjangoObjectType

from roles.graphql.roles import PermissionNode
from users.models import User
from users.services.user_service import UserService
from utils.decorators import login_required
from utils.exceptions import ValidationGraphQLError


class UserNode(DjangoObjectType):
    id = graphene.ID(source="pk", required=True)
    permissions = graphene.List(PermissionNode)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "is_superuser",
            "is_verified",
            "role",
            "phone",
        )

    def resolve_permissions(self, info):
        return self.user_permissions.all()


class UpdateMeInput(graphene.InputObjectType):
    first_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    phone = graphene.String(required=False)


class UpdateMe(graphene.Mutation):
    user = graphene.Field(UserNode)

    class Arguments:
        input = UpdateMeInput(required=True)

    @login_required
    def mutate(self, info, input: UpdateMeInput):
        try:
            user = UserService.update_user(
                info.context.user,
                first_name=input.first_name,
                last_name=input.last_name,
                phone=input.phone,
            )
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return UpdateMe(user=user)


class Query(graphene.ObjectType):
    me = graphene.Field(UserNode)

    @login_required
    def resolve_me(self, info):
        return info.context.user


class Mutation(graphene.ObjectType):
    update_me = UpdateMe.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
