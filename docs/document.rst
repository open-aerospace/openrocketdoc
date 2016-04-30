===============
Rocket Document
===============

Rocket
======

The basic structure of a rocket document is a "Rocket" type as the root:

.. autoclass:: openrocketdoc.document.Rocket
    :members:
    :show-inheritance:

The rocket is divided into stages:

Stage
=====

.. autoclass:: openrocketdoc.document.Stage
    :members:
    :show-inheritance:

A stage is a collection of components


Components:
===========

Types of components available to describe a rocket stage:

Nosecone
--------

.. autoclass:: openrocketdoc.document.Nosecone
    :members:
    :inherited-members:
    :show-inheritance:

.. autoclass:: openrocketdoc.document.Noseshape
    :members:
    :undoc-members:

Bodytube
--------

.. autoclass:: openrocketdoc.document.Bodytube
    :members:
    :inherited-members:
    :show-inheritance:

Mass
----

.. autoclass:: openrocketdoc.document.Mass
    :members:
    :inherited-members:
    :show-inheritance:

Fin
---

.. autoclass:: openrocketdoc.document.Fin
    :members:
    :inherited-members:
    :show-inheritance:

Finset
------

.. autoclass:: openrocketdoc.document.Finset
    :members:
    :inherited-members:
    :show-inheritance:


Engine
======

.. autoclass:: openrocketdoc.document.Engine
    :members:
    :inherited-members:
    :show-inheritance:
