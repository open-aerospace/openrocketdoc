# -*- coding: utf-8 -*-
from enum import Enum
import copy
from math import pi, atan, tan, radians, degrees, log


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
    """Top level of an Open Rocket Document. A Rocket is made of stages.

    :param `str` name: Name of the rocket

    **Members:**
    """

    def __init__(self, name):
        self.name = name
        """Name of this rocket"""

        self.stages = []
        """List of stages that makes up the rocket."""

    @property
    def mass(self):
        """**[kg]** Get the total *dry* mass of the rocket"""
        return sum(stage.mass for stage in self.stages)


class Stage(object):
    """One Stage of a Rocket.

    :param `str` name: Name of the stage.

    **Members:**
    """

    def __init__(self, name):
        self.name = name
        """Name of the stage."""

        self.components = []
        """A list of components that make up the stage."""

    @property
    def mass(self):
        """**[kg]** Get the total *dry* mass of this stage"""
        return sum(c.mass for c in self.components)


class Component(object):
    """A Component is a piece of the rocket like a fin or nosecone.
    """

    def __init__(self, name, mass=0.0, length=0.0, diameter=0.0, material_name=""):
        self.name = name
        """Name"""

        self.length = length
        """**[m]** Length"""

        self.diameter = diameter
        """**[m]** Diameter"""

        self._mass = mass
        self._color = None
        self._material_name = material_name

        self.components = []
        """List of components inside this component."""

        self.tags = []
        """A list of tags that may describe this component."""

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
        """**[kg]** The total *dry mass* of this component, **including all
        subcomponents**.
        """
        return self._mass + sum([c.mass for c in self.components])

    @mass.setter
    def mass(self, m):
        self._mass = float(m)

    @property
    def component_mass(self):
        """**[kg]** The *dry mass* of just this component.
        """
        return self._mass

    @property
    def color(self):
        """The color (if defined) of this component.
        """
        return self._color

    @color.setter
    def color(self, c):
        """Set the color of this component.
        """
        self._color = c

    @property
    def material_name(self):
        """The name of the main material this component is made of.
        Example: "Aluminium" or "440 Stainless". This is not used directly,
        but rather is for descriptive purposes.
        """
        return self._material_name

    @material_name.setter
    def material_name(self, name):
        self._material_name = name


class Mass(Component):
    """Generic mass component. This is a catch-all for internal structure that
    contributes to the mass model of the rocket but doesn't serve a specific
    purpose to be modeled. Often you know some internal detail like a flange or
    flight computer that is heavy, but it doesn't contribute to the
    aerodynamics. When in doubt use this. Give it a descriptive name!

    Defining a Mass component requires a name and a mass. Many optional
    arguments can be set that are used to compute, for example, density.

    :param `str` name: name of this mass
    :param `float [kg]` mass: mass of the component
    :\**kwargs:
        * **[m] length** (`float`) overall length of the mass
        * **[m] diameter** (`float`) greatest diameter of the mass
        * **material_name** (`str`) name of the main material this component is made of.

    :example:

    >>> from openrocketdoc.document import *
    >>> Mass("Flight Computer", 0.0215)
    <openrocketdoc.document.Mass "Flight Computer" (0.02 kg)>

    **Members:**

    """

    def __init__(self, name, mass, **kwargs):
        super(Mass, self).__init__(name, mass=mass, **kwargs)

    def __repr__(self):
        return "<openrocketdoc.document.Mass \"%s\" (%0.2f kg)>" % (self.name, self.mass)


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
        * **material_name** (`str`) name of the main material this component is made of.

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
        """**[μm]** The surface roughness of the Nose
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
        * **material_name** (`str`) name of the main material this component is made of.

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
        """**[μm]** The surface roughness of the Body tube.
        """
        return self._roughness

    @surface_roughness.setter
    def surface_roughness(self, r):
        self._roughness = r

    @property
    def surface_area(self):
        """**[m²]** Surface area (skin of the vehicle)
        """
        return pi * self.diameter * self.length

    @property
    def density(self):
        """**[kg/m³]** The average material density of the tube
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
    """A single fin.

    Almost all sounding rockets have a set of fins near the base of the
    vehicle. This class represents a single fin. If there are multiple
    symmetric fins, an :class:`.Finset` can be used to handle replication.

    Fins are assumed to be trapezoidal (Truncated delta wings). To define a fin
    you need to know the length of several chords. The Fin takes the Root
    Chord, Tip Chord and span (height) of the fin.

    The fin sweep can either be defined as a distance (from the start of the
    fin to the beginning of the tip) or as the angle the leading edge of the
    fin makes with respect to the body of the rocket. Do not set both of these
    at the same time, rather set the one convenient for you.

    :param `str` name: The name of this fin
    :param `float [m]` root: Length of the Root Chord
    :param `float [m]` tip: Length of the Tip Chord
    :param `float [m]` span: Length of height of the fin away from the rocket
                             body
    :param `float [m]` sweep: (Optional) Distance from the start of the
                              fin to the beginning of the tip
    :param `float [°]` sweepangle: (Optional) Angle the leading edge of the
                                   fin makes with respect to the body of the
                                   rocket.

    :example:

    >>> from openrocketdoc.document import *
    >>> Fin("My Fin", 0.5, 0.24, 0.4, sweepangle=45.0)
    <openrocketdoc.document.Fin "My Fin">

    **Members:**
    """

    def __init__(self, name, root, tip, span, sweep=None, sweepangle=45.0, **kwargs):
        super(Fin, self).__init__(name, length=root, **kwargs)

        self.root = root
        """**[m]** The Root Chord of the Fin"""

        self.tip = tip
        """**[m]** The Tip Chord of the Fin"""

        self.span = span
        """**[m]** Height of the fin away from the rocket body"""

        self._sweep = sweep
        self._sweepangle = sweepangle

    def __repr__(self):
        return "<openrocketdoc.document.Fin \"%s\">" % (self.name)

    @property
    def sweep(self):
        """**[m]** The Distance from the start of the fin to the beginning of
        the tip.
        """
        if self._sweep is not None:
            return self._sweep
        return self.span * tan(radians(self._sweepangle))

    @sweep.setter
    def sweep(self, s):
        self._sweep = s

    @property
    def sweepangle(self):
        """**[°]** Angle the leading edge of the fin makes with respect to the
        body of the rocket.
        """
        if self._sweep is not None:
            return degrees(atan(self._sweep / self.span))
        return self._sweepangle

    @sweepangle.setter
    def sweepangle(self, s):
        self._sweep = None
        self._sweepangle = s


class Finset(Component):
    """A set of identical fins, set symmetrically around the vehicle.

    For convince and "Don't Repeat Yourself" sake, a identical, symmetric set
    of fins can be defined as a single "finset". Build a single :class:`.Fin`
    object, and pass that to the constructor of this class along with the
    number of fins, and the full finset is built for you.

    :param `str` name: Name of the component
    :param `Fin` fin: A single Fin object to be repeated as part of the set
    :param `int` number_of_fins: Number of fins in the set

    :example:

    >>> from openrocketdoc.document import *
    >>> a_fin = Fin("My Fin", 0.5, 0.24, 0.4, sweepangle=45.0)
    >>> Finset("Fins", a_fin, 3)
    <openrocketdoc.document.Finset "Fins" (3 fins)>

    **Members:**
    """

    def __init__(self, name, fin, number_of_fins, **kwargs):
        super(Finset, self).__init__(name, **kwargs)

        self._fin = fin
        self.number_of_fins = number_of_fins

    def __repr__(self):
        return "<openrocketdoc.document.Finset \"%s\" (%d fins)>" % (self.name, self.number_of_fins)

    @property
    def number_of_fins(self):
        """The number of fins in the finset.
        """
        return len(self.components)

    @number_of_fins.setter
    def number_of_fins(self, n):
        self.components = []

        # Build a copy of the fin object
        for i in range(n):
            fin_copy = copy.deepcopy(self._fin)
            fin_copy.name = "Fin %d" % (i + 1)
            self.components.append(fin_copy)

    @property
    def fin(self):
        """A single fin prototype. Update this to update all fins to a new fin object.
        """
        return self._fin

    @fin.setter
    def fin(self, fin):
        self._fin = fin
        # rebuild finset
        self.number_of_fins = len(self.components)


class Engine(object):
    """The business end of the rocket.

    This class can define either the bulk properties of the engine (like total
    thrust and Isp) or define a thrustcuve as a function of time. If a
    thurstcuve is provided then the bulk numbers are computed from the curve.
    If no curve is provided then a simple thrustcuve (flat) is computed.

    Test if the class is constrained (that is, enough information is provided to
    fully solve a thrustcurve) using Engine.constrained (returns a boolean)

    :param str name: Name of this engine.

    **Members:**
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

    @property
    def length(self):
        """**[m]** Length of the engine, be that the actual length of a self-contained
        solid motor, or the whole system length of a liquid fuel system tanks
        and all.
        """
        if self._length is not None:
            return self._length

        # if no length is set directly, report it being the length of the system
        l = sum([tank['length'] for tank in self.tanks])
        return l

    @length.setter
    def length(self, l):
        self._length = l

    @property
    def diameter(self):
        """**[m]** Diameter of the engine system
        """
        if self._diameter is not None:
            return self._diameter

        # if no diameter is set directly, report it being the max diameter of the system
        if self.tanks:
            return max([tank['diameter'] for tank in self.tanks])
        return 0

    @diameter.setter
    def diameter(self, val):
        self._diameter = val

    @property
    def Isp(self):
        """**[s]** Average Specific Impulse (Isp) of the engine. Either computed from a
        thrust curve or can be set directly and used to compute theoretical
        performance numbers based on chemistry.
        """
        if self._Isp is not None:
            return self._Isp
        if self.m_prop > 0:
            return self.I_total/(self.m_prop * 9.80665)
        return 0

    @Isp.setter
    def Isp(self, val):
        self._Isp = val

    @property
    def m_prop(self):
        """**[kg]** Mass of the propellent in a loaded engine. This is total mass of
        the fuel and oxidiser.
        """

        # Trivial case, we already know the exact mass
        if type(self._m_fuel) is float and type(self._m_ox) is float:
            return self._m_fuel + self._m_ox

        # We might know enough to compute:
        if self._Isp is not None and self._thrust_avg is not None and self._t_burn is not None:
            mdot = self._thrust_avg / (self.V_e)
            return mdot * self._t_burn

        if self._m_fuel is None and self._m_ox is None:
            return 0
        if self._m_fuel is None:
            return self._m_ox
        if self._m_ox is None:
            return self._m_fuel

    @m_prop.setter
    def m_prop(self, val):
        # we must not know much about the system
        self._m_fuel = val / 2.0
        self._m_ox = val / 2.0

    @property
    def thrust_avg(self):
        """**[N]** Average thrust of the motor over the length of it's nominal burn.
        Either computed from a thrust curve, or can be set directly to use in
        computing desired performance.
        """
        # if we know the burntime and total impulse then we can compute
        # otherwise return the value stored in _thrust_avg
        # other-otherwise give up (return 0)
        if not self.thrustcurve:
            if self._thrust_avg is not None:
                return self._thrust_avg
            return 0
        return self.I_total / self.t_burn

    @thrust_avg.setter
    def thrust_avg(self, val):
        # set this directly if a thrustcurve isn't available
        self._thrust_avg = val

    @property
    def I_total(self):
        """**[N·s]** Total impulse of the engine over a nominal burn. Either computer
        from a thrust curve, or can be set directly to use in computing
        desired performance.
        """
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

        # If we know thrust and time
        if self.thrust_avg > 0 and self.t_burn > 0:
            return self.thrust_avg * self.t_burn

        # compute from ISP and mass
        if self._Isp is not None:
            return self.m_prop * self.V_e

        return 0

    @I_total.setter
    def I_total(self, val):
        self._I_total = val

    @property
    def t_burn(self):
        """**[s]** Burn time. The time that it takes to burn all the propellent in a
        nominal burn. Either computed from a thrust curve or can be set directly for
        computing desired performance.
        """

        # if we have a thrust curve, compute directly
        if self.thrustcurve:
            return self.thrustcurve[-1]['t']

        # compute from average thrust, ISP and mass
        if self.V_e > 0 and self.m_prop > 0:
            mdot = self.thrust_avg / (self.V_e)
            return self.m_prop / mdot

        # else try the override value, else give up (return 0)
        if self._t_burn is not None:
            return self._t_burn
        return 0

    @t_burn.setter
    def t_burn(self, val):
        self._t_burn = val

    @property
    def thrust_peak(self):
        """**[N]** Peak thrust during a nominal burn.
        """
        if self.thrustcurve:
            return max([t['thrust'] for t in self.thrustcurve])

        if self._thrust_peak is not None:
            return self._thrust_peak

        if self._thrust_avg is not None:
            return self._thrust_avg

        return 0

    @thrust_peak.setter
    def thrust_peak(self, val):
        self._thrust_peak = val

    @property
    def m_frac(self):
        """[unitless] Mass fraction of the engine system. The ratio of the
        loaded mass of the engine system and the empty weight. Often an
        important figure of merit in designing a rocket.
        """
        if self.m_init > 0:
            return (self.m_prop / self.m_init) * 100.0
        return 0

    @m_frac.setter
    def m_frac(self, val):
        self._m_frac = val

    @property
    def V_e(self):
        """**[m/s]** Effective velocity (average) of the exhaust gasses of the
        engine.
        """
        return self.Isp * 9.80665

    @V_e.setter
    def V_e(self, val):
        self._Isp = val / 9.80665

    @property
    def m_init(self):
        """**[kg]** Initial weight of the engine system, including propellent.
        """
        m_tanks = sum([tank['mass'] for tank in self.tanks])
        return self.m_prop + m_tanks + self._m_system

    @property
    def nar_code(self):
        """The NAR code for a rocket motor is a letter code for the total
        impulse.
        """

        if self.I_total <= 0:
            return ''

        # how many times we double 2.5 Ns
        nar_i = int(log(self.I_total/2.5)/log(2))

        # ASCII math :)
        if nar_i < 26:
            return chr(66 + nar_i)
        return 'A' + chr(66 + nar_i - 26)

    @property
    def nar_percent(self):
        """What percent of the NAR impulse class is the motor
        """
        nar_i = int(log(self.I_total/2.5)/log(2))

        max_class = (2.5*2**(nar_i+1))
        min_class = (2.5*2**nar_i)

        nar_percent = (self.I_total - min_class)/(max_class - min_class)
        return nar_percent * 100.0

    @property
    def constrained(self):
        """Is the system fully described?

        :rtype: boolean
        """
        if self.I_total > 0:
            return True
        return False
