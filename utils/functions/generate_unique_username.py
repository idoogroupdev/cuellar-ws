from users.models import User
from utils.functions.random_username import random_username


def generate_unique_username(email: str, extra_characters=5):
    while True:
        username = random_username(email, extra_characters)
        if not User.objects.filter(username=username).exists():
            return username
