import math

import graphene
from graphene import relay
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay.connection.array_connection import cursor_to_offset


class ConnectionField(DjangoFilterConnectionField):
    @classmethod
    def resolve_connection(cls, connection_type, args, iterable, max_limit=None):
        connection = super().resolve_connection(
            connection_type,
            args,
            iterable,
            max_limit,
        )

        connection._pagination_args = args

        return connection


class PaginationInfo(graphene.ObjectType):
    total_count = graphene.Int(required=True)
    current_page = graphene.Int(required=True)
    total_pages = graphene.Int(required=True)
    has_previous_page = graphene.Boolean(required=True)
    has_next_page = graphene.Boolean(required=True)


class BaseConnection(relay.Connection):
    pagination = graphene.Field(PaginationInfo)

    class Meta:
        abstract = True

    @staticmethod
    def resolve_pagination(root, info):
        args = getattr(root, "_pagination_args", {})

        first = args.get("first", 10)
        after = args.get("after")
        offset = 0

        if after:
            offset = cursor_to_offset(after) + 1

        total_count = root.length

        total_pages = math.ceil(total_count / first)
        current_page = (offset // first) + 1

        return PaginationInfo(
            total_count=total_count,
            total_pages=total_pages,
            current_page=current_page,
            has_previous_page=offset > 0,
            has_next_page=(offset + first) < total_count,
        )
