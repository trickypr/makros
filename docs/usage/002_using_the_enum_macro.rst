####################
Using the enum macro
####################

The enum macro provides a significantly more powerful alternative to the python
`enum <https://docs.python.org/3/library/enum.html>`_ module. First, create a
file called `enum.mpy`. This is where we will be experimenting with the enum. It
should have the following contents:

.. code-block:: python

    macro import enum

    enum Animals:
        Dog
        Cat
        Bird
        Other(name: str)

This file will be converted to the following code:

.. code-block:: python

    # Macro imported: enum

    class Animals:
        def __assign_enum_types__(Animals, dog, cat, bird, other):
            Animals.Dog = dog
            Animals.Cat = cat
            Animals.Bird = bird
            Animals.Other = other
        
        def __eq__(self, other):
            return isinstance(self, other)


    class Dog(Animals):
        def __str__(self):
            return 'Dog'


    class Cat(Animals):
        def __str__(self):
            return 'Cat'


    class Bird(Animals):
        def __str__(self):
            return 'Bird'


    class Other(Animals):
        def __init__(self, name: str):
            self.name = name
        
        def __str__(self):
            return f'Other(name: {self.name})'

    Animals.__assign_enum_types__(Animals, Dog, Cat, Bird, Other)

    del(Dog)
    del(Cat)
    del(Bird)
    del(Other)

You do not have to understand the purpose of this code, just that, under the
hood, an enum is represented as a number of classes.

You can compare these against the enum to determine their type.

.. code-block:: python
    
    # Continued from first example...

    animal_1 = Animals.Cat
    animal_2 = Animals.Other("Lion")

    assert animal_1 == Animals.Cat
    assert animal_2 == Animals.Other

    assert animal_1 != animal_2

    print(animal_2.name)

Most of this behavior is fairly normal. The most important part to note is that
the value of a generic enum is ignored. This mean any ``Animal.Other`` will be
equal to any other ``Animal.Other``

Properties on generic enums are accessed via ``enum.property_name``. So in this
example, the property is accessed via ``animal_2.name``.

A copy of this example code is available on `GitHub <https://github.com/trickypr/makros/tree/main/examples/002_using_the_enum_macro>`_.

