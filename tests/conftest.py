import pytest

from roles.management.commands import setup_roles as setup_roles_command


@pytest.fixture
def setup_system_roles():
    setup_roles_command.Command().handle()
