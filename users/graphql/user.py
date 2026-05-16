import graphene
from graphene_django import DjangoObjectType

from roles.graphql.roles import PermissionNode, RoleNode
from users.models import User
from utils.decorators import login_required


class UserNode(DjangoObjectType):
    id = graphene.ID(source="pk", required=True)
    roles = graphene.List(RoleNode)
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
        )

    def resolve_roles(self, info):
        return self.roles.all()

    def resolve_permissions(self, info):
        return self.user_permissions.all()


class Query(graphene.ObjectType):
    me = graphene.Field(UserNode)

    @login_required
    def resolve_me(self, info):
        return info.context.user


schema = graphene.Schema(query=Query)
