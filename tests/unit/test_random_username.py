from utils.functions.random_username import random_username


def test_random_username():
    assert len(random_username("test@test.com")) == 9
