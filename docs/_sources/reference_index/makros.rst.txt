###########
Makros Core
###########

These should be used for implementing Makros into a third party build system.
They should be imported from the module root:

.. code-block:: python

    from makros import Makros

It is recommended to use the higher level functions like ``translate_file`` and
``translate_folder`` in your projects as they will experience smaller api changes,
but the ``Makros`` object will provide the most flexibility. You should avoid
creating instances of ``MakroParser`` directly, instead creating it via ``Makros``.

.. currentmodule:: makros

.. autosummary::
    :toctree: ../reference

    ~Makros
    ~MakroParser
    ~translate_file
    ~translate_folder
