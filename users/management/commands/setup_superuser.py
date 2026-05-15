from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

from roles.models import DefaultSystemRole
from users.models import User


class Command(BaseCommand):
    help = "Setup initial superuser"

    def handle(self, *args, **options):
        self.setup_superuser()

    def setup_superuser(self):
        """Create the first admin user."""

        try:
            if User.objects.count() == 0:
                user = User.objects.create_superuser(
                    username="superuser",
                    email=settings.SUPERUSER_EMAIL,
                    password=settings.SUPERUSER_PASSWORD,
                )

                user.groups.set([Group.objects.get(name=DefaultSystemRole.ADMIN.value)])

                self.stdout.write(self.style.SUCCESS("Successfully setup admin user"))

        except IntegrityError:
            self.stdout.write(self.style.ERROR("Admin user already exists"))
