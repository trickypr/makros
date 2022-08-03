# Macro imported: namespace

# Start of namespace test

class namespace_test:
    def __init__(self):
        def hello():
            print("Hello, World!")
        
        self.hello = hello

test = namespace_test()
del namespace_test
# End of namespace test
test.hello()