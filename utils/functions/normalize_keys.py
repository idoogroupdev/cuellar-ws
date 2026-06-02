def snake_to_camel(value: str) -> str:
    parts = value.split("_")
    return parts[0] + "".join(part.capitalize() for part in parts[1:])


def normalize_keys(data: dict, function=snake_to_camel) -> dict:
    return {function(key): value for key, value in data.items()}
