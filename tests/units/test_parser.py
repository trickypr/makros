from pathlib import Path
from makros.makros import Makros


class TestParser:
    def test_parse_string(self):
        parser = Makros.get().get_parser(Path('./internal.mpy'))
        
        output = parser.parse_string("""macro import namespace

namespace store:
    store_contents = {}

    def load_store():
        print("Loading from store...")
    
    def save_store():
        print("Saving to store...")
    
    export def set(key, value):
        store_contents[key] = value
        save_store()
    
    export def get(key):
        return store_contents[key]
    
    load_store()


# Set and get a key
store.set('test', 'Hello world!')
print(store.get('test'))""")

        assert output == """# Macro imported: namespace

# Start of namespace store

class namespace_store:
    def __init__(self):
        store_contents = {}
        
        def load_store():
        
            print("Loading from store...")
        
        def save_store():
        
            print("Saving to store...")
        
        def set(key, value):
            store_contents[key] = value
        
            save_store()
        
        def get(key):
            return store_contents[key]
        
        self.set = set
        self.get = get

store = namespace_store()
del namespace_store
# End of namespace store
store.set('test', 'Hello world!')
print(store.get('test'))
"""