from utils.functions.normalize_keys import normalize_keys


def test_normalize_keys():
    data = {
        "first_name": "Juan",
        "last_name": "Perez",
        "is_active": True,
        "is_staff_user": True,
    }

    assert normalize_keys(data) == {
        "firstName": "Juan",
        "lastName": "Perez",
        "isActive": True,
        "isStaffUser": True,
    }
