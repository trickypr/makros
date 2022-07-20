# Macro imported: namespace

# Start of namespace test

class __test_namespace_creator:
    def __init__(self):
        def hello():
            print("Hello, World!")
        
        self.hello = hello

test = __test_namespace_creator()
del __test_namespace_creator


# End of namespace test
test.hello()