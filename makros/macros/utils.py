import re

pattern = re.compile(r'(?<!^)(?=[A-Z])')


def camel_to_snake(name: str) -> str:
    return pattern.sub('_', name).lower()
