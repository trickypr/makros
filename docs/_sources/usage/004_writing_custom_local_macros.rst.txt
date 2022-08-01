#############################
Writing custom macros locally
#############################

Prerequisites
=============
- Decent python knowledge
- An understanding of recursive decent parsing - See `Crafting Interpreters <https://craftinginterpreters.com/parsing-expressions.html>`_

This program includes the ability for you to write your own macros. Whilst these
macros can be published to pypi, it is often easier to develop them locally. 

First create a folder with the name of the macro that you would like to import. 
For example, if you were writing a set of macros called greet, you would create 
a folder called ``greet/``. In that folder create a file called ``macros.json`` 
with this contents, and the templates replaced:

.. code-block:: json

    {
        "name": "{NAME}",
        "package": "{FOLDER_NAME}",
        "description": "{MACRO_DESCRIPTION}",
        "macros": [],
        "bootstrap": []
    }


To create a macro, you will need to create a ``.py`` or ``.mpy`` file in the folder.
If the file is a ``.mpy`` file, you will need to add it to the bootstrap array.
Then add the macro to the macros array:

.. code-block:: json

    {
        "name": "Greeter",
        "package": "greet",
        "description": "A selection of greeting macros",
        "macros": [
            {
                "name": "Hello",
                "keyword": "hello",
                "file": "hello.mpy",
                "description": "Say hello to someone"
            }
        ],
        "bootstrap": ["hello.mpy"]
    }

From here, we can start to write out parser. Whilst the ``makros`` package
provides a number of helper libraries, it leaves the parsing up to you. Whilst
you can use any parsing technique, this program has been developed to be
familiar to anyone who has completed the fist interpreter inside of the 
`Crafting interpreters book <https://craftinginterpreters.com/>`.

The first part of a macro is the parser, which must extend the ``MacroParser``
class and have the name ``Parser``. This function will be responsible for
parsing your code. The example for this project will be fairly simple, but full
blown parers, `like the one used for namespaces <https://github.com/trickypr/makros/blob/main/src/macros/namespace.mpy>`_
or `enums <https://github.com/trickypr/makros/blob/main/src/macros/enum.py>`_
may be necessary for more complex projects.

.. code-block:: python

    from makros.macros.types import MacroParser, MacroTranslator
    from makros.tokens import Tokens
    import tokenize

    class Parser(MacroParser):
        def parse(self, tokens: Tokens) -> any:
            token = tokens.advance()

            token_return = '""'

            if token.type == tokenize.STRING:
                token_return = token.string.replace("'", '"')
            
            if token.type == tokenize.NAME:
                token_return = token.string
            
            return token_return

This example will provide a string to the translator, but it is often necessary
to send a more complex AST tree to the translator. Because it is just a string,
our parsing code can be fairly neat:

.. code-block:: python

    class Translator(MacroTranslator):
        def translate(self, token_return: str) -> str:
            return "print(f'Hello, {" + token_return + "}')"

This is now a complete custom macro. You can import it in your project so long
as the folder is within your project tree. You can then use it in your code:

.. code-block:: python

    macro import greet.hello
    hello "World"

You can publish your macro to pypi and the makro command will index it by package
name. Complete source code for this example is `available on GitHub <https://github.com/trickypr/makros/tree/main/examples/004_writing_custom_local_macros>`_.
