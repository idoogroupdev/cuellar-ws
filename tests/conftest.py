import pytest
from graphene_django.utils.testing import graphql_query

from roles.management.commands import setup_roles as setup_roles_command


@pytest.fixture
def setup_system_roles():
    setup_roles_command.Command().handle()


@pytest.fixture
def client_query(client, setup_system_roles):
    def func(*args, **kwargs):
        return graphql_query(*args, **kwargs, client=client)

    return func
