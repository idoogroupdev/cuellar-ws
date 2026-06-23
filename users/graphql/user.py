import graphene
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django_filters import OrderingFilter
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload

from roles.graphql.roles import PermissionNode
from users.models import CashbackHistory, User
from users.services.user_service import UserService
from utils.decorators import login_required, permission_required, staff_member_required
from utils.exceptions import ValidationGraphQLError
from utils.filters import FullFilterSet
from utils.graphql import BaseConnection, ConnectionField


class UserNode(DjangoObjectType):
    id = graphene.ID(source="pk", required=True)
    permissions = graphene.List(PermissionNode)
    cashback_balance = graphene.Decimal()

    class Meta:
        model = User
        exclude = (
            "password",
            "last_login",
            "state",
            "date_joined",
            "user_permissions",
            "session_version",
        )
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        connection_class = BaseConnection

    def resolve_permissions(self, info):
        return Permission.objects.filter(group__in=self.groups.all()).distinct()

    def resolve_profile_image(self, info):
        return self.profile_image.url if self.profile_image else None

    def resolve_cashback_balance(self, info):
        return CashbackHistory.objects.filter(user_id=self.id).cashback_balance()


class UserFilter(FullFilterSet):
    order_by = OrderingFilter(
        fields=(
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "is_active",
            "id",
            "is_staff",
        )
    )

    class Meta:
        model = User
        fields = {
            "first_name": ["icontains"],
            "last_name": ["icontains"],
            "email": ["icontains"],
            "date_joined": ["icontains"],
            "role__name": ["exact"],
            "phone": ["icontains"],
        }
        or_fields = {
            "first_name": ["icontains"],
            "last_name": ["icontains"],
            "email": ["icontains"],
            "phone": ["icontains"],
        }


class UpdateMeInput(graphene.InputObjectType):
    first_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    phone = graphene.String(required=False)
    profile_image = Upload(required=False)


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
                profile_image=input.profile_image,
            )
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return UpdateMe(user=user)


class CreateUserInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    role_name = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=False)
    phone = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    branch_id = graphene.ID(required=False)


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserNode)

    class Arguments:
        input = CreateUserInput(required=True)

    @staff_member_required
    @permission_required(User, ["add"])
    def mutate(self, info, input: CreateUserInput):
        try:
            user = UserService.create_user(
                email=input.email.lower(),
                password=input.password,
                role_name=input.role_name,
                branch_id=input.branch_id,
                first_name=input.first_name,
                last_name=input.last_name,
                phone=input.phone,
                is_active=input.is_active,
                is_verified=True,
            )
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return CreateUser(user=user)


class UpdateUserInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    role_name = graphene.String(required=False)
    first_name = graphene.String(required=False)
    last_name = graphene.String(required=False)
    phone = graphene.String(required=False)
    is_active = graphene.Boolean(required=False)
    branch_id = graphene.ID(required=False)


class UpdateUser(graphene.Mutation):
    user = graphene.Field(UserNode)

    class Arguments:
        input = UpdateUserInput(required=True)

    @staff_member_required
    @permission_required(User, ["change"])
    def mutate(self, info, input: UpdateUserInput):
        user = User.objects.filter(pk=input.id).first()

        if not user:
            message = _("User not found.")
            raise ValidationGraphQLError(fields={"id": [message]}, message=message)

        try:
            kwargs = dict(input.items())
            kwargs.pop("id", None)

            user = UserService.update_user(user, **kwargs)
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return UpdateUser(user=user)


class Query(graphene.ObjectType):
    me = graphene.Field(UserNode)
    all_users = ConnectionField(UserNode, filterset_class=UserFilter)

    @login_required
    def resolve_me(self, info):
        return info.context.user

    @staff_member_required
    @permission_required(User, ["view"])
    def resolve_all_users(self, info, **kwargs):
        return User.objects.all()


class Mutation(graphene.ObjectType):
    update_me = UpdateMe.Field()
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
