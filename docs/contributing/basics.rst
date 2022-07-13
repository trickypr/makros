##########################
Getting started developing
##########################

Prerequisites
=============
 - Python knowledge
 - Git experience
 - A `fork of makros <https://github.com/trickypr/makros/fork>`_ cloned to your local computer
 - `Poetry installed <https://python-poetry.org/docs/>`_

Setting up the build environment
================================

First, create a new branch for your feature. You can either do this with your
git client or by running the following command.

.. code-block:: bash

    git checkout -b feature/my-feature

Next, install the projects dependencies and enter into the virtual environment.

.. code-block:: bash

    poetry install
    poetry shell

Writing tests
=============

Before implementing a feature or fixing a bug, you should write tests that cover
the new feature or bug. There are two different types of tests that are used
inside this project, ``macro`` tests and ``unit`` tests. Macro tests are macro
files that are transpiled and executed to make sure that macro parsing, 
translation and execution works as expected. Unit tests are tests that are
for exported functions and classes, like the `Tokens` class.

Macro tests
-----------

To add a new macro test, crate a new ``.mpy`` file inside of ``tests/macros``.
The test runner will automatically pick this up and generate a new test for you.

Unit tests
----------
Unit tests are written using `pytest <https://docs.pytest.org/en/7.1.x/>`_.
Follow their documentation for a guide on how to write your tests

Running tests
-------------
We have a custom test runner than can be invoked by running:

.. code-block:: bash

    python tests
