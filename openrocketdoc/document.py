# -*- coding: utf-8 -*-


class Rocket(object):
    """Rocket Object. Contains list of stages"""
    def __init__(self, name):
        self.name = name
        self.stages = []

    @property
    def mass(self):
        return sum(stage.mass for stage in self.stages)


class Stage(object):
    """One Stage of a Rocket. Contains list of components"""
    def __init__(self, name):
        self.name = name
        self.components = []

    @property
    def mass(self):
        return sum(c.mass for c in self.components)


class Component(object):
    """A Component is a piece of the rocket like a fin or noesecone."""

    def __init__(self, name, mass=0.0, length=0.0):
        self.name = name
        self.mass = mass
        self.length = length


class Nosecone(Component):
    """Nose of the rocket. There can only be one"""

    def __init__(self, **kwargs):
        super(Nosecone, self).__init__("Nosecone", **kwargs)
        self.shape = ''
        self.thickness = 0


class Bodytube(Component):
    """docstring for Bodytube"""

    def __init__(self, name, **kwargs):
        super(Bodytube, self).__init__(name, **kwargs)


class Fin(Component):
    """A single rocket fin"""

    def __init__(self, **kwargs):
        super(Fin, self).__init__("Fin", **kwargs)
