import secrets
import string

from django.db.models import Model


def random_digits(length=6):
    return "".join(secrets.choice(string.digits) for _ in range(length))


def random_alphanumeric(length=6):
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def generate_unique_code(
    model: Model,
    length=6,
    is_alphanumeric=False,
    field_name: str = "code",
):

    if not hasattr(model, field_name):
        raise ValueError(f"Field {field_name} not found in {model}")

    while True:
        code = random_alphanumeric(length) if is_alphanumeric else random_digits(length)

        if not model.objects.filter(**{field_name: code}).exists():
            return code
