def program(*args) -> str:
    return '\n'.join(args)


def create_func(name: str, args: str, body: str) -> str:
    return f'''def {name}({args}):
{indent(body)}
'''


def create_class(name: str, body: str, extends: str = None) -> str:
    return f'''
class {name}{f"({extends})" if extends else ""}:
{indent(body)}
'''


def indent(text: str, indentation: str = '    ') -> str:
    return '\n'.join(indentation + line for line in text.splitlines())