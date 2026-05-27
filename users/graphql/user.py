import graphene
from django.core.exceptions import ValidationError
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload

from roles.graphql.roles import PermissionNode
from users.models import User
from users.services.user_service import UserService
from utils.decorators import login_required, permission_required, staff_member_required
from utils.exceptions import ValidationGraphQLError


class UserNode(DjangoObjectType):
    id = graphene.ID(source="pk", required=True)
    permissions = graphene.List(PermissionNode)

    class Meta:
        model = User
        exclude = ("password", "last_login", "state", "date_joined")

    def resolve_permissions(self, info):
        return self.user_permissions.all()

    def resolve_profile_image(self, info):
        return self.profile_image.url if self.profile_image else None


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


class CreateStaffUserInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    role_name = graphene.String(required=True)
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=False)
    phone = graphene.String(required=False)


class CreateStaffUser(graphene.Mutation):
    user = graphene.Field(UserNode)

    class Arguments:
        input = CreateStaffUserInput(required=True)

    @staff_member_required
    @permission_required(User, ["add"])
    def mutate(self, info, input: CreateStaffUserInput):
        try:
            user = UserService.create_user_with_role(
                email=input.email.lower(),
                password=input.password,
                role_name=input.role_name,
                first_name=input.first_name,
                last_name=input.last_name,
                phone=input.phone,
                is_staff=True,
                is_verified=True,
            )
        except ValidationError as exc:
            raise ValidationGraphQLError(fields=exc.message_dict)

        return CreateStaffUser(user=user)


class Query(graphene.ObjectType):
    me = graphene.Field(UserNode)

    @login_required
    def resolve_me(self, info):
        return info.context.user


class Mutation(graphene.ObjectType):
    update_me = UpdateMe.Field()
    create_staff_user = CreateStaffUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
