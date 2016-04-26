# -*- coding: utf-8 -*-

from __future__ import print_function
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import openrocketdoc.document as rdoc


class RockSimEngine(object):
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
        {'name': u"Inital Weight", 'key': 'initWt', 'type': float, 'convert': 1e-3},
        {'name': u"Mass fraction", 'key': 'massFrac', 'type': float},
        {'name': u"Manafacturer", 'key': 'mfg', 'type': str},
        {'name': u"Peak thrust", 'key': 'peakThrust', 'type': float},
        {'name': u"Thoat diameter", 'key': 'throatDia', 'type': float, 'convert': 1e-3},
        {'name': u"Propellent weight", 'key': 'propWt', 'type': float, 'convert': 1e-3},
        {'name': u"Length", 'key': 'len', 'type': float, 'convert': 1e-3},
    ]

    def __init__(self):
        self.engine = {}

    def load(self, filelike):
        with open(filelike) as fin:
            root = ET.fromstring(fin.read())
            engine = root[0][0]

            for definition in self.rse_engine_defs:
                if definition['type'] is float:
                    # grab number out of XML
                    val = float(engine.get(definition['key']))
                    # convert to MKS
                    val = val * definition.get('convert', 1)  # default to 1 for no conversion factor
                    self.engine[definition['name']] = val
                else:
                    self.engine[definition['name']] = engine.get(definition['key'])

            for element in engine:
                if element.tag == "comments":
                    self.engine["Comments"] = element.text
                if element.tag == "data":
                    self.engine["Thrustcurve"] = []
                    for datapoint in element:
                        time = float(datapoint.get('t'))
                        thrust = float(datapoint.get('f'))
                        mass = float(datapoint.get('m')) / 1000.0  # convert to kilograms
                        cg = float(datapoint.get('cg')) / 1000.0  # convert to meters
                        self.engine["Thrustcurve"].append({'t': time, 'thrust': thrust, 'mass': mass, 'cg': cg})


class Openrocket(object):
    """Loader for OpenRocket files.

    :returns: Openrocket instance

    Example::

        import openrocketdoc
        ork = openrocketdoc.loaders.Openrocket()
        ork.load('rocket.ork')

    """

    # list of OpenRocket parts we care about
    part_types = [
        'nosecone',
        'bodytube',
        'trapezoidfinset',
        'masscomponent',
        'streamer',
        'centeringring',
        'engineblock',
    ]

    def __init__(self):
        pass

    def _subcomponent_walk(self, tree):
        """My mom always said, never loop when you can recurse"""

        for subcomponent in tree:
            component = {}
            if subcomponent.tag in self.part_types:
                component['type'] = subcomponent.tag
                for meta in subcomponent:
                    if meta.tag == 'subcomponents':
                        component['parts'] = [sub for sub in self._subcomponent_walk(meta)]
                if subcomponent.tag == 'nosecone':
                    component['data'] = rdoc.Nosecone(rdoc.Noseshape.CONE)
                    for desc in subcomponent:
                        if desc.tag == 'name':
                            component['data'].name = desc.text
                        if desc.tag == 'length':
                            component['data'].length = float(desc.text)
                        if desc.tag == 'shape':
                            component['data'].shape = desc.text
                        if desc.tag == 'thickness':
                            component['data'].thickness = desc.text

                component['data'] = component.get('data', rdoc.Component("name")).__dict__
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
        stages = []
        for base in root:
            if base.tag == 'rocket':
                for orkrocket in base:
                    if orkrocket.tag == 'name':
                        rocket_name = orkrocket.text
                    if orkrocket.tag == 'subcomponents':
                        for orkstage in orkrocket:
                            if orkstage.tag == 'stage':
                                name = "stage {0}".format(len(stages))
                                for _tag in orkstage:
                                    if _tag.tag == 'name':
                                        name = _tag.text
                                stage = {'name': name, 'parts': [part for part in self._subcomponent_walk(orkstage)]}
                            stages.append(stage)

        self.rocket = {'name': rocket_name, 'stages': stages}
