# Macro imported: enum

class Test:
    def __assign_enum_types__(a, b):
        Test.A = a
        Test.B = b


class A(Test):
    pass


class B(Test):
    def __init__(self, val1: str, val2: str):
        self.val1 = val1
        self.val2 = val2

Test.__assign_enum_types__(A, B)


test1 = Test.A()
print(isinstance(test1, Test.A))
