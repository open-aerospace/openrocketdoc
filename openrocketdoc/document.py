# -*- coding: utf-8 -*-
from enum import Enum
Noseshape = Enum('Noseshape', 'CONE VONKARMAN')


class Rocket(object):
    """A top level Rocket object.

    :param str name: Name of the rocket

    """

    def __init__(self, name):
        self.name = name
        #: List of stages that make up the rocket
        self.stages = []

    @property
    def mass(self):
        """Get the total **dry mass** of the rocket"""
        return sum(stage.mass for stage in self.stages)


class Stage(object):
    """One Stage of a Rocket.

    :param str name: Name of a stage

    """
    def __init__(self, name):
        self.name = name
        #: List of components (nose, body, fins, etc.) that make up stage
        self.components = []

    @property
    def mass(self):
        """Get the total **dry mass** of this stage"""
        return sum(c.mass for c in self.components)


class Component(object):
    """A Component is a piece of the rocket like a fin or noesecone."""

    def __init__(self, name, mass=0.0, length=0.0):
        self.name = name
        #: Dry mass of the component
        self.mass = mass
        self.length = length


class Nosecone(Component):
    """Nose of the rocket. There can only be one per rocket

    :param str shape: Shape of the nosecone

    """

    def __init__(self, shape, **kwargs):
        super(Nosecone, self).__init__("Nosecone", **kwargs)
        self.shape = shape
        self.thickness = 0


class Bodytube(Component):
    """docstring for Bodytube"""

    def __init__(self, name, **kwargs):
        super(Bodytube, self).__init__(name, **kwargs)


class Fin(Component):
    """A single rocket fin"""

    def __init__(self, **kwargs):
        super(Fin, self).__init__("Fin", **kwargs)
