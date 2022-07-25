#########################
Using the namespace macro
#########################

The namespace macro allows you to contain the scope of your code without needing
to write a new file. It is modeled based off of `the Typescript <https://www.typescriptlang.org/docs/handbook/namespaces.html>`_ 
``namespace`` feature

.. code-block:: python

    macro import namespace

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
    
We can then access the functions that are exported from the namespace. For
example, the ``set`` and ``get`` keys.

.. code-block:: python

    # Set and get a key
    store.set('test', 'Hello world!')
    print(store.get('test'))

However, you cannot call functions that are not exported. In this example, you
cannot run the ``load_store`` and ``save_store`` functions.

.. code-block:: python

    # You cannot access unexported keys
    store.load_store() # This will error
    store.save_store() # This will error

Note that you cannot export variables at the current time due to the structure
of the program. If you want this, you may open a pull request with the feature 
to `the Github repo <https://github.com/trickypr/makros>`_.