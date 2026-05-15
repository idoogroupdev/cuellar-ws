from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from roles.models import DefaultSystemRole, Role


def create_permission_groups(roles: dict):
    for role_name, models_perms in roles.items():
        group, _ = Group.objects.get_or_create(name=role_name)

        desired_perms = set()

        for model, actions in models_perms.items():
            content_type = ContentType.objects.get_for_model(model)
            for action in actions:
                codename = f"{action}_{model._meta.model_name}"
                try:
                    perm = Permission.objects.get(
                        content_type=content_type, codename=codename
                    )
                    desired_perms.add(perm)
                except Permission.DoesNotExist:
                    print(
                        f"[WARN] Permission {codename} does not exist for {model.__name__}"
                    )

        current_perms = set(group.permissions.all())

        to_add = desired_perms - current_perms
        if to_add:
            group.permissions.add(*to_add)

        to_remove = current_perms - desired_perms
        if to_remove:
            group.permissions.remove(*to_remove)

        Role.objects.update_or_create(name=role_name, defaults={"group": group})

        print(
            f"[SYNC] Group '{role_name}': +{len(to_add)} permissions, -{len(to_remove)} permissions"
        )


class Command(BaseCommand):
    help = "Setup initial roles"

    def handle(self, *args, **options):

        self.all_permissions = ["view", "change", "delete", "add"]

        self.setup_client()
        self.setup_salesperson()
        self.setup_delivery()
        self.setup_admin()
        self.setup_operator()

    def setup_client(self):

        roles = {DefaultSystemRole.CLIENT.value: {}}

        create_permission_groups(roles)

    def setup_salesperson(self):

        roles = {DefaultSystemRole.SALESPERSON.value: {}}

        create_permission_groups(roles)

    def setup_delivery(self):

        roles = {DefaultSystemRole.DELIVERY.value: {}}

        create_permission_groups(roles)

    def setup_admin(self):

        roles = {DefaultSystemRole.ADMIN.value: {}}

        create_permission_groups(roles)

    def setup_operator(self):

        roles = {DefaultSystemRole.OPERATOR.value: {}}

        create_permission_groups(roles)
