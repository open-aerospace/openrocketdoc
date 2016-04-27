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


class Engine(object):
    """The business end of the rocket.

    This class can define either the bulk properties of the engine (like total
    thrust and Isp) or define a thrustcuve as a function of time. If a
    thurstcuve is provided then the bulk numbers are computed from the curve.
    If no curve is provided then a simple thrustcuve (flat) is computed.

    Test if the class is constrained (that is, enough information is provided to
    fully solve a thrustcurve) using Engine.constrained (returns a boolean)

    """

    def __init__(self, name):
        self.name = name
        self.manufacturer = ""
        self.comments = ""
        self.throat_diameter = 0

        self._Isp = None
        self._length = None
        self._diameter = None
        self._I_total = None
        self._thrust_avg = None
        self._thrust_peak = None
        self._t_burn = None
        self._mass_frac = None
        self._m_fuel = None
        self._m_ox = None
        self._m_system = 0

        self.tanks = []
        self.thrustcurve = []

    def __repr__(self):
        return '<openrocketdoc.document.Engine "%s">' % self.name

    def get_length(self):
        if self._length is not None:
            return self._length

        # if no length is set directly, report it being the length of the system
        l = sum([tank['length'] for tank in self.tanks])
        return l

    def set_length(self, l):
        self._length = l

    def get_diameter(self):
        if self._diameter is not None:
            return self._diameter

        # if no diameter is set directly, report it being the max diameter of the system
        if self.tanks:
            return max([tank['diameter'] for tank in self.tanks])
        return 0

    def set_diameter(self, val):
        self._diameter = val

    def get_isp(self):
        return self.I_total/(self.m_prop * 9.80665)

    def set_isp(self, val):
        self._Isp = val

    def get_m_prop(self):
        if type(self._m_fuel) is float and type(self._m_ox) is float:
            return self._m_fuel + self._m_ox
        if self._m_fuel is None and self._m_ox is None:
            return 0
        if self._m_fuel is None:
            return self._m_ox
        if self._m_ox is None:
            return self._m_fuel

    def set_m_prop(self, val):
        # we must not know much about the system
        self._m_fuel = val / 2.0
        self._m_ox = val / 2.0

    def get_thrust_avg(self):
        # if we know the burntime and total impulse then we can compute
        # otherwise return the value stored in _thrust_avg
        # other-otherwise give up (return 0)
        if self.t_burn <= 0:
            if self._thrust_avg is not None:
                return self._thrust_avg
            return 0
        return self.I_total / self.t_burn

    def set_thrust_avg(self, val):
        # set this directly if a thrustcurve isn't available
        self._thrust_avg = val

    def get_I_total(self):
        # if we have a thrust curve, compute directly
        if self.thrustcurve:
            # Trapezoidal rule numeric ingratiation
            itot = 0
            for i, t in enumerate(self.thrustcurve[:-1]):
                x = t['t']
                x_1 = self.thrustcurve[i+1]['t']
                f_x = t['thrust']
                f_x1 = self.thrustcurve[i+1]['thrust']
                itot += (x_1 - x) * (f_x1 + f_x)
            return itot / 2.0

        # else try the override value, else give up (return 0)
        if self._I_total is not None:
            return self._I_total
        return 0

    def set_I_total(self, val):
        self._I_total = val

    def get_t_burn(self):
        # if we have a thrust curve, compute directly
        if self.thrustcurve:
            return self.thrustcurve[-1]['t']
        # else try the override value, else give up (return 0)
        if self._t_burn is not None:
            return self._t_burn
        return 0

    def set_t_burn(self, val):
        self._t_burn = val

    def get_thrust_peak(self):
        if self.thrustcurve:
            return max([t['thrust'] for t in self.thrustcurve])

        if self._thrust_peak is not None:
            return self._thrust_peak
        return 0

    def set_thrust_peak(self, val):
        self._thrust_peak = val

    def get_m_frac(self):
        return (self.m_prop / self.m_init) * 100.0

    def set_m_frac(self, val):
        self._m_frac = val

    length = property(get_length, set_length)
    diameter = property(get_diameter, set_diameter)
    Isp = property(get_isp, set_isp)
    m_prop = property(get_m_prop, set_m_prop)
    thrust_avg = property(get_thrust_avg, set_thrust_avg)
    I_total = property(get_I_total, set_I_total)
    t_burn = property(get_t_burn, set_t_burn)
    thrust_peak = property(get_thrust_peak, set_thrust_peak)
    m_frac = property(get_m_frac, set_m_frac)

    @property
    def m_init(self):
        m_tanks = sum([tank['mass'] for tank in self.tanks])
        return self.m_prop + m_tanks + self._m_system

    @property
    def constrained(self):
        if self.I_total > 0:
            return True
        return False
