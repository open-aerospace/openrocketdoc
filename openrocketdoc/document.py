# -*- coding: utf-8 -*-
from enum import Enum
import copy
from math import pi


class Noseshape(Enum):
    """Enum defining possible shapes of a nosecone.
    """

    CONE = 1
    """A simple cone.
    """

    SPHERE_BLUNTED_CONE = 2
    """A Cone with a spherically blunt tip
    """

    BICONIC = 3
    """A Cone with a conically blunted tip
    """

    TANGENT_OGIVE = 4
    """A nosecone defined as tangent (to body) set of ogives
    """

    SECANT_OGIVE = 5
    """An ovgive nose not tangent to body
    """

    SPHERE_BLUNTED_OGIVE = 6
    """A tangent ogive cone with a spherically blunted tip
    """

    ELLIPTICAL = 7
    """A nose that is one half of an ellipse
    """

    PARABOLIC = 8
    """Similar to elliptical nose, but made of a parabola rather then ellipse
    """

    VONKARMAN = 9
    """The Von Karman nosecone is a kind of optimzed nosecone shape. It's
    formed by a Haack series (C = 0) giving minimum drag for the given length and diameter.
    """

    POWER_SERIES = 10
    """Cone edges are defined by a set of polynomial equations.

    For n = 0..1: y = R(x/L)^n

    * n = 1 is cone
    * n = 0.75 for a 3/4 power
    * n = 0.5 for a 1/2 power (parabola)
    * n = 0 for a cylinder
    """

    HAACK_SERIES = 11
    """Cone edges are defined by minimal-drag Sears–Haack body with constant C

    * C = 1/3 for LV-Haack
    * C = 0 for LD-Haack, defined as Von Karman
    """


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
    """A Component is a piece of the rocket like a fin or nosecone.
    """

    def __init__(self, name, mass=0.0, length=0.0, diameter=0.0):
        self.name = name
        self._mass = mass
        self.length = length
        self.diameter = diameter
        self._color = None

        #: List of sub components
        self.components = []

        #: List of optional tags
        self.tags = []

    def add_class_tag(self, newclass, newtag):
        """Add a new tag that is part of a tag collection (class)

        :param str newclass: class that the tag is a member of
        :param str tag: the tag to add

        """

        for tag in self.tags:
            if type(tag) is dict:
                if tag['class'] == newclass:
                    tag['tags'].append(newtag)
                    return

        self.tags.append({'class': newclass, 'tags': [newtag]})

    @property
    def mass(self):
        """Get the total *dry mass* of this component, **including all subcomponents**.
        """
        return self._mass + sum([c.mass for c in self.components])

    @mass.setter
    def mass(self, m):
        self._mass = float(m)

    @property
    def component_mass(self):
        """Get the *dry mass* of just this component.
        """
        return self._mass

    @property
    def color(self):
        """Get the color (if defined) of this component.
        """
        return self._color

    @color.setter
    def color(self, c):
        """Set the color of this component.
        """
        self._color = c


class Mass(Component):
    """Generic mass component. This is a catch-all for internal structure that
    contributes to the mass model of the rocket but doesn't serve a specific
    purpose to be modeled.

    :param `str` name: name of this mass
    """

    def __init__(self, name, **kwargs):
        super(Mass, self).__init__(name, **kwargs)


class Nosecone(Component):
    """Nose of the rocket. Nosecones come in many shapes. See the
    :class:`.Noseshape` for nosecone shapes that can be described by this
    module.

    In general a Nosecone is the first component in the top stage. It's defined
    by a "shape", like a cone or an ogive, and an optional shape parameter used
    to further define the exact shape. The very tip of the Nosecone is used as
    the reference location (0 coordinate) for the rest of the rocket.

    Defining a Nosecone requires a shape, shape parameter, mass, and length. 0
    is a valid number if mass or length is not known yet, though most
    properties of the nose will not be computed in that case. Diameter is an
    optional parameter, and is often not set directly because it depends on
    another part of the rocket (e.g, the overall radius of the vehicle being
    modeled, input later).

    :param `Noseshape` shape: Shape of the nosecone
    :param `float` shape_parameter: Many nosecone types need a unitless number --
                                   to describe their construction. See :class:`.Noseshape` for details
    :param `float [kg]` mass: Dry mass of the nosecone
    :param `float [m]` length: Tip to base (not including internal structure) length of the nosecone
    :\**kwargs:
        * **[m] diameter** (`float`) diameter at the base

    :example:

    >>> from openrocketdoc.document import *
    >>> Nosecone(Noseshape.CONE, 0.7, 1.2, diameter=0.254)
    <openrocketdoc.document.Nosecone (0.70 kg)>

    **Members:**
    """

    def __init__(self, shape, shape_parameter, mass, length, **kwargs):
        super(Nosecone, self).__init__("Nosecone", length=length, mass=mass, **kwargs)
        self.shape = shape
        self.shape_parameter = shape_parameter
        self.thickness = 0
        self._roughness = 0

    def __repr__(self):
        return "<openrocketdoc.document.Nosecone (%0.2f kg)>" % (self.mass)

    @property
    def surface_roughness(self):
        """The surface roughness of the Nose (in microns)
        """
        return self._roughness

    @surface_roughness.setter
    def surface_roughness(self, r):
        self._roughness = r


class Bodytube(Component):
    """A cylindrical section of the outer body of the rocket.

    The main part of a rocket is going to be a long cylindrical tube.

    A name, the mass and length are required. 0 is a valid number if mass or
    length is not known yet, though most properties of the component will not
    be computed in that case. Diameter is an optional parameter, and is often
    not set directly because it depends on another part of the rocket (e.g, the
    overall radius of the vehicle being modeled, input later).


    :param str name: Name of the component
    :param `float [kg]` mass: Dry mass of this section of body
    :param `float [m]` length: Length of this section of body
    :\**kwargs:
        * **[m] diameter** (`float`) diameter at the base

    :example:

    >>> from openrocketdoc.document import *
    >>> Bodytube("My Tube", 1.2, 0.538)
    <openrocketdoc.document.Bodytube "My Tube" (1.20 kg)>

    **Members:**
    """

    def __init__(self, name, mass, length, **kwargs):
        super(Bodytube, self).__init__(name, mass=mass, length=length, **kwargs)
        self._roughness = 0
        self.thickness = 0
        self._density = None

    def __repr__(self):
        return "<openrocketdoc.document.Bodytube \"%s\" (%0.2f kg)>" % (self.name, self.mass)

    @property
    def surface_roughness(self):
        """The surface roughness of the Body tube (in microns)
        """
        return self._roughness

    @surface_roughness.setter
    def surface_roughness(self, r):
        self._roughness = r

    @property
    def surface_area(self):
        """Surface area (skin of the vehicle)
        """
        return pi * self.diameter * self.length

    @property
    def density(self):
        """The average material density of the tube
        """
        if self._density is not None and self._mass == 0:
            return self._density
        if self.thickness > 0:
            r1 = self.diameter / 2.0
            r2 = r1 - self.thickness
            return self.component_mass / (pi * self.length * (r1**2 + r2**2))
        return 0

    @density.setter
    def density(self, d):
        self._density = d


class Fin(Component):
    """A single rocket fin"""

    def __init__(self, name, **kwargs):
        super(Fin, self).__init__(name, **kwargs)

        self.root = 0
        self.tip = 0
        self.span = 0
        self.sweep = None
        self.sweepangle = 0


class Finset(Component):
    """A set of identical fins, set symetrically around the vehicle.

    :param str name: Name of the compenent
    :param Fin fin: A single Fin object to be repeated as part of the set
    :param int number_of_fins: Number of fins in the set
    """

    def __init__(self, name, fin, number_of_fins, **kwargs):
        super(Finset, self).__init__(name, **kwargs)

        for i in range(number_of_fins):
            fin_copy = copy.deepcopy(fin)
            fin_copy.name = "Fin %d" % (i + 1)
            self.components.append(fin_copy)


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

    def thrust(self, t):
        if not self.thrustcurve:
            return self.thrust_avg

    def make_thrustcurve(self, points=3):
        tc = []
        if not self.thrustcurve:
            t_inc = self.t_burn / float(points)
            for i in range(points):
                t = i * t_inc
                tc.append({'t': t, 'thrust': self.thrust(0)})
        else:
            tc = self.thrustcurve
        return tc

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
        if self._Isp is not None:
            return self._Isp
        if self.m_prop > 0:
            return self.I_total/(self.m_prop * 9.80665)
        return 0

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
        if not self.thrustcurve:
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

        # else try the override value
        if self._I_total is not None:
            return self._I_total

        # compute from ISP and mass
        if self._Isp is not None:
            return self.m_prop * self.V_e
        return 0

    def set_I_total(self, val):
        self._I_total = val

    def get_t_burn(self):
        # if we have a thrust curve, compute directly
        if self.thrustcurve:
            return self.thrustcurve[-1]['t']

        # compute from average thrust, ISP and mass
        if self.V_e > 0:
            mdot = self.thrust_avg / (self.V_e)
            return self.m_prop / mdot

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
        if self.m_init > 0:
            return (self.m_prop / self.m_init) * 100.0
        return 0

    def set_m_frac(self, val):
        self._m_frac = val

    def get_ve(self):
        return self.Isp * 9.80665

    def set_ve(self, val):
        self._Isp = val / 9.80665

    length = property(get_length, set_length)
    diameter = property(get_diameter, set_diameter)
    Isp = property(get_isp, set_isp)
    m_prop = property(get_m_prop, set_m_prop)
    thrust_avg = property(get_thrust_avg, set_thrust_avg)
    I_total = property(get_I_total, set_I_total)
    t_burn = property(get_t_burn, set_t_burn)
    thrust_peak = property(get_thrust_peak, set_thrust_peak)
    m_frac = property(get_m_frac, set_m_frac)
    V_e = property(get_ve, set_ve)

    @property
    def m_init(self):
        m_tanks = sum([tank['mass'] for tank in self.tanks])
        return self.m_prop + m_tanks + self._m_system

    @property
    def constrained(self):
        if self.I_total > 0:
            return True
        return False
