import random
import string

from utils.functions.username_from_email import username_from_email


def random_username(email: str, extra_characters=5):
    username = username_from_email(email)

    characters = string.ascii_lowercase + string.digits
    random_str = "".join(random.choice(characters) for _ in range(extra_characters))  # nosec

    return f"{username}{random_str}"
