###############
Getting started
###############

Prerequisites
=============
- Python and Pip

Installing
==========
Makros can be installed via pip like any other python package by running:

.. code-block:: bash

    pip install makros

Writing your first code
=======================
By default makros behaves the same way they python interpreter does. A simple
hello world example will look the same within makros or python:

.. code-block:: python

    print("Hello World!")

But from here, you are able to include "macros" in your code. Macros are parsers
that extend what you can do with Python whilst still maintaining compatibility.
For example, there is a makro that allows you to create namespaces:

.. code-block:: python
    
    macro import namespace
    
    namespace hello:
        export def world():
            print("Hello World!")
    
    hello.world() # Should print out "Hello World!"

This can then be run via the makros command in your terminal

.. code-block:: bash

    makros file_path.mpy

This will convert your ``.mpy`` file into a ``.py`` python file. It will also
run the file right away. 