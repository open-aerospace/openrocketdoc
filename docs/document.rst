===============
Rocket Document
===============

Rocket
======

The basic structure of a rocket document is a "Rocket" type as the root:

.. autoclass:: openrocketdoc.document.Rocket
    :members:


The rocket is divided into stages:

Stage
=====

.. autoclass:: openrocketdoc.document.Stage
    :members:

A stage is a collection of components:


Components:
===========

Types of components available to describe a rocket stage:

Nosecone
--------

.. autoclass:: openrocketdoc.document.Nosecone
    :members:
    :inherited-members:
    :undoc-members:

.. autoclass:: openrocketdoc.document.Noseshape
    :members:


Bodytube
--------

.. autoclass:: openrocketdoc.document.Bodytube
    :members:
    :inherited-members:

Mass
----

.. autoclass:: openrocketdoc.document.Mass
    :members:
    :inherited-members:

Fin
---

.. autoclass:: openrocketdoc.document.Fin
    :members:
    :inherited-members:

Finset
------

.. autoclass:: openrocketdoc.document.Finset
    :members:
    :inherited-members:


Engine
======

.. autoclass:: openrocketdoc.document.Engine
    :members:
    :inherited-members:

