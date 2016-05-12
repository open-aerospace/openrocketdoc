# -*- coding: utf-8 -*-

from __future__ import print_function
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import openrocketdoc.document as rdoc


class FilelikeLoader(object):
    """Baseclass for classes that will load a file, or file-like object. We
    test to see if the passed object looks like a filehandle, or just a
    filename.
    """

    def load(self, filelike):
        """Parse the file into a OpenRocketDoc representation.

        :param filelike filelike: File handle or str filename to open and parse
        """

        if hasattr(filelike, 'read'):
            # it's probably a file handler, or something like that
            return self._load(filelike.read())
        elif type(filelike) is str and len(filelike) > 255:
            # it's maybe a str containing the file contents?
            return self._load(filelike)
        else:
            # maybe a filename?
            try:
                with open(filelike, 'r') as fh:
                    return self._load(fh.read())
            except IOError:
                # or not
                return self._load(filelike)


class RaspEngine(FilelikeLoader):
    """File loader for RASP engine files (.eng)
    """

    def __init__(self):
        self.engine = rdoc.Engine("Imported RASP Egine")

    def _load(self, file_str):
        comments = ""
        start_data = False  # flag to throw after we finish reading the header
        for line in file_str.split('\n'):
            if len(line) < 1:
                continue  # blank line
            if line[0] == ';':
                if not start_data:
                    comments += line[1:] + "\n"
            else:
                if not start_data:
                    # This is the first data line, has metadata

                    # RASP engine data is space-delimited
                    fields = line.split(' ')

                    # Fields are positional
                    self.engine.name = fields[0]
                    self.engine.manufacturer = fields[6].strip()
                    self.engine.m_prop = float(fields[4])

                    # build a "tank" the size of the solid motor
                    self.engine.tanks.append({
                        "mass": float(fields[5]) - float(fields[4]),  # initial weight - propellent weight
                        "length": float(fields[2]) / 1000.0,          # convert to meters
                        "diameter": float(fields[1]) / 1000.0,        # convert to meters
                    })

                    # After we read the first data line, know the rest is thrust curve
                    start_data = True
                else:
                    # Thrustcuve data:
                    if any(char.isdigit() for char in line):
                        fields = line.split(' ')
                        time = float(fields[0].strip())
                        thrust = float(fields[1].strip())
                        self.engine.thrustcurve.append({'t': time, 'thrust': thrust})

        self.engine.comments = comments
        return self.engine


class RockSimEngine(FilelikeLoader):
    """File Loader for RockSim engine files (.rse).

    RockSim Engine files are XML.
    """

    rse_engine_defs = [
        {'name': u"Isp", 'key': 'Isp', 'type': float},
        {'name': u"Total impulse", 'key': 'Itot', 'type': float},
        {'name': u"Average thrust", 'key': 'avgThrust', 'type': float},
        {'name': u"Burn time", 'key': 'burn-time', 'type': float},
        {'name': u"Name", 'key': 'code', 'type': str},
        {'name': u"Diameter", 'key': 'dia', 'type': float, 'convert': 1e-3},
        {'name': u"Exit diameter", 'key': 'exitDia', 'type': float, 'convert': 1e-3},
        {'name': u"Initial weight", 'key': 'initWt', 'type': float, 'convert': 1e-3},
        {'name': u"Mass fraction", 'key': 'massFrac', 'type': float},
        {'name': u"Manufacturer", 'key': 'mfg', 'type': str},
        {'name': u"Peak thrust", 'key': 'peakThrust', 'type': float},
        {'name': u"Throat diameter", 'key': 'throatDia', 'type': float, 'convert': 1e-3},
        {'name': u"Propellent weight", 'key': 'propWt', 'type': float, 'convert': 1e-3},
        {'name': u"Length", 'key': 'len', 'type': float, 'convert': 1e-3},
    ]

    def __init__(self):
        self.engine = rdoc.Engine("Imported RockSim Engine")

    def _load(self, filestr):
        root = ET.fromstring(filestr)
        rse = root[0][0]
        rse_dict = {}

        for definition in self.rse_engine_defs:
            if definition['type'] is float:
                # grab number out of XML
                val = float(rse.get(definition['key']))
                # convert to MKS
                val = val * definition.get('convert', 1)  # default to 1 for no conversion factor
                rse_dict[definition['name']] = val
            else:
                rse_dict[definition['name']] = rse.get(definition['key'])

        # Build rdoc engine from rse defs
        self.engine.name = rse_dict["Name"]
        self.engine.manufacturer = rse_dict["Manufacturer"]

        # we don't know the mixture ratio, just set total propellent mass directly
        self.engine.m_prop = rse_dict["Propellent weight"]

        # Assuming simple solid motor, there is one "tank", it's the casing.
        self.engine.tanks.append({
            "mass": rse_dict["Initial weight"] - rse_dict["Propellent weight"],
            "length": rse_dict["Length"],
            "diameter": rse_dict["Diameter"],
        })

        for element in rse:
            if element.tag == "comments":
                self.engine.comments = element.text
            if element.tag == "data":
                for datapoint in element:
                    time = float(datapoint.get('t'))
                    thrust = float(datapoint.get('f'))
                    mass = float(datapoint.get('m', 0)) / 1000.0  # convert to kilograms
                    cg = float(datapoint.get('cg', 0)) / 1000.0  # convert to meters
                    self.engine.thrustcurve.append({'t': time, 'thrust': thrust, 'mass': mass, 'cg': cg})

        return self.engine


class Openrocket(object):
    """Loader for OpenRocket files.

    :returns: Openrocket instance

    Example::

        import openrocketdoc
        ork = openrocketdoc.loaders.Openrocket()
        ork.load('rocket.ork')

    """

    def __init__(self):
        pass

    def _load_nosecone(tree):
        # defaults:
        shape = rdoc.Noseshape.CONE
        length = 0
        thickness = 0
        diameter = 0
        mass = 0
        color = None
        or_tags = []

        # Read data
        for element in tree:
            if element.tag == 'shape':
                shape_str = element.text
                if 'ogive' in shape_str.lower():
                    shape = rdoc.Noseshape.TANGENT_OGIVE
                elif 'cone' in shape_str.lower():
                    shape = rdoc.Noseshape.CONE
            if element.tag is 'shapeparameter':
                pass  # TODO: set shapeparameter
            if element.tag == 'length':
                length = float(element.text)
            if element.tag == 'thickness':
                thickness = float(element.text)
            if element.tag == 'aftradius':
                if 'auto' not in element.text:
                    diameter = float(element.text) * 2
            if element.tag == 'color':
                r = int(element.get('red', 0))
                g = int(element.get('green', 0))
                b = int(element.get('blue', 0))
                color = (r, g, b)
            if element.tag == 'linestyle':
                or_tags.append("linestyle:"+element.text)

        nose = rdoc.Nosecone(shape, mass, length)
        nose.thickness = thickness
        nose.diameter = diameter
        if color is not None:
            nose.color = color

        for tag in or_tags:
            nose.add_class_tag('OpenRocket', tag)

        return nose

    def _load_bodytube(tree):
        tube = rdoc.Bodytube('bodytube')

        # Read data
        for element in tree:
            if element.tag == 'name':
                tube.name = element.text
            if element.tag == 'length':
                tube.length = float(element.text)
            if element.tag == 'color':
                r = int(element.get('red', 0))
                g = int(element.get('green', 0))
                b = int(element.get('blue', 0))
                tube.color = (r, g, b)

        return tube

    def _load_mass(tree):
        mass = rdoc.Mass('mass')

        # Read data
        for element in tree:
            if element.tag == 'name':
                mass.name = element.text
            if element.tag == 'mass':
                mass._mass = float(element.text)
            if element.tag == 'position':
                mass.center = float(element.text)
            if element.tag == 'packedlength':
                mass.length = float(element.text)
            if element.tag == 'color':
                r = int(element.get('red', 0))
                g = int(element.get('green', 0))
                b = int(element.get('blue', 0))
                mass.color = (r, g, b)

        return mass

    def _load_fins(tree):
        fins = rdoc.Fin('fin')

        return fins

    def _load_finset(tree):
        fin = rdoc.Fin('Fin')
        number_of_fins = 0
        name = "Finset"

        for element in tree:
            if element.tag == 'name':
                name = element.text
            if element.tag == 'rootchord':
                fin.root = float(element.text)
            if element.tag == 'tipchord':
                fin.tip = float(element.text)
            if element.tag == 'height':
                fin.span = float(element.text)
            if element.tag == 'sweeplength':
                fin.sweeplength = float(element.text)
            if element.tag == 'fincount':
                number_of_fins = int(element.text)
            if element.tag == 'color':
                r = int(element.get('red', 0))
                g = int(element.get('green', 0))
                b = int(element.get('blue', 0))
                fin.color = (r, g, b)

        finset = rdoc.Finset(name, fin, number_of_fins)

        return finset

    def _subcomponent_walk(self, tree):
        """My mom always said, never loop when you can recurse"""

        for subcomponent in tree:
            # We'll only decode things we know about
            if subcomponent.tag in self.part_types.keys():

                component = self.part_types[subcomponent.tag](subcomponent)

                for element in subcomponent:
                    if element.tag == 'subcomponents':
                        component.components = [sub for sub in self._subcomponent_walk(element)]

                yield component
            elif subcomponent.tag == 'subcomponents':
                yield [sub for sub in self._subcomponent_walk(subcomponent)]

    def load(self, filename):
        """Read an OpenRocket file"""

        zf = ZipFile(filename)
        root = ET.fromstring(zf.read(zf.namelist()[0]))

        self.or_version = root.attrib['version']

        # Walk tree, there should be a 'rocket' and 'simulation tags'. We only
        # care about 'rocket'. After that there is a little metadata and then
        # components.
        for element in root:
            if element.tag == 'rocket':

                # We found a rocket! Create a document
                ordoc = rdoc.Rocket("Imported OpenRocket File")  # default name

                for orkrocket in element:
                    if orkrocket.tag == 'name':
                        # This rocket has a name
                        ordoc.name = orkrocket.text

                    if orkrocket.tag == 'subcomponents':
                        # This rocket has stages
                        for orkstage in orkrocket:
                            if orkstage.tag == 'stage':
                                # Create a stage, default name is stage number
                                stage = rdoc.Stage("stage {0}".format(len(ordoc.stages)))

                                for stage_parts in orkstage:
                                    if stage_parts.tag == 'name':
                                        stage.name = stage_parts.text
                                    if stage_parts.tag == 'subcomponents':
                                        # Recurse down through all components
                                        stage.components = [part for part in self._subcomponent_walk(stage_parts)]

                                # Append to rocket
                                ordoc.stages.append(stage)

        return ordoc

    # list of OpenRocket parts we care about
    part_types = {
        'nosecone': _load_nosecone,
        'bodytube': _load_bodytube,
        'masscomponent': _load_mass,
        'trapezoidfinset': _load_finset,
        # 'streamer',
        # 'centeringring',
        # 'engineblock',
    }
