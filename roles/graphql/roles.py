import graphene
from django.contrib.auth.models import Permission
from graphene_django import DjangoObjectType

from roles.models import Role


class RoleNode(DjangoObjectType):
    id = graphene.ID(source="pk", required=True)

    class Meta:
        model = Role
        fields = ("name",)


class PermissionNode(DjangoObjectType):
    id = graphene.ID(source="pk", required=True)

    class Meta:
        model = Permission
        fields = ("codename",)
