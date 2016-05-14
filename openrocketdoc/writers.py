# -*- coding: utf-8 -*-

from __future__ import print_function
from openrocketdoc import document as rdoc
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from yaml import dump as yamldump


class Document(object):
    """Write Open Rocket Doc
    """

    def __init__(self):
        pass

    def _component_dict(self, component):
        """For recursively building a tree of components.
        """

        # All must have name and type
        c = {'name': component.name}
        c['type'] = component.__class__.__name__

        # All components have mass, length, diameter
        c['mass'] = component.component_mass
        c['length'] = component.length
        c['diameter'] = component.diameter

        # All components have optional tags
        c['tags'] = component.tags

        # Type specific writers:
        if type(component) is rdoc.Nosecone:
            c['shape'] = component.shape.name
            c['shape_parameter'] = component.shape_parameter
            c['thickness'] = component.thickness
            c['surface'] = component.surface_roughness

        elif type(component) is rdoc.Fin:
            c['root_chord'] = component.root
            c['tip_chord'] = component.tip
            c['span'] = component.span
            c['sweepangle'] = component.sweepangle

        # recursion
        if component.components:
            c['components'] = []
            for subcomponent in component.components:
                c['components'].append(self._component_dict(subcomponent))

        return c

    def dump(self, ordoc):
        """Return a string yaml formated native Open Rocket Doc
        """

        # We want some control over what is printed
        # (not a naive dump of everything in every object)
        # So we build a dictionary first

        doc = {}

        # rocket top level
        if type(ordoc) is rdoc.Rocket:
            doc['rocket'] = {'name': ordoc.name}
            doc['rocket']['stages'] = []
            for stage in ordoc.stages:
                s = {'name': stage.name}
                s['components'] = []
                for component in stage.components:
                    s['components'].append(self._component_dict(component))
                doc['rocket']['stages'].append(s)

        return yamldump(doc, default_flow_style=False)


class RaspEngine(object):
    """Write a RASP engine file format

    Members:
    """

    def __init__(self):
        pass

    def dump(self, engine):
        """Return a str of the file output

        :param openrocketdoc.document.Engine engine: The OpenRocketDoc engine to write
        :returns: (str) formated file

        """

        # comments
        doc = ";"
        doc += engine.comments.replace('\n', "\n;")
        doc += '\n'

        # header
        doc += ' '.join([
            engine.name.replace(' ', '-'),
            "%0.0f" % (engine.diameter * 1000),
            "%0.0f" % (engine.length * 1000),
            "0",
            "%0.4f" % (engine.m_prop),
            "%0.4f" % (engine.m_init),
            engine.manufacturer.replace(' ', '-'),
        ])
        doc += '\n'

        if not engine.thrustcurve:
            for element in engine.make_thrustcurve():
                doc += "%0.3f %0.3f\n" % (element['t'], element['thrust'])
        for element in engine.thrustcurve:
            doc += "%0.3f %0.3f\n" % (element['t'], element['thrust'])

        return doc


class RockSimEngine(object):
    """RockSim Engine file format writter
    """

    def __init__(self):
        pass

    def dump(self, engine):
        """Return a str of the file

        :param openrocketdoc.document.Engine engine: The OpenRocketDoc engine to write
        :returns: (str) formated file
        """

        doc = ET.Element('engine-database')

        eng_list = ET.SubElement(doc, 'engine-list')

        # Engine metadata
        eng = ET.SubElement(eng_list, 'engine')
        eng.attrib['code'] = engine.name
        eng.attrib['mfg'] = engine.manufacturer
        eng.attrib['len'] = "%0.0f" % (engine.length * 1000.0)     # to mm
        eng.attrib['dia'] = "%0.0f" % (engine.diameter * 1000.0)   # to mm
        eng.attrib['Isp'] = "%0.1f" % engine.Isp
        eng.attrib['Itot'] = "%0.3f" % engine.I_total
        eng.attrib['avgThrust'] = "%0.1f" % engine.thrust_avg
        eng.attrib['peakThrust'] = "%0.1f" % engine.thrust_peak
        eng.attrib['burn-time'] = "%0.2f" % engine.t_burn
        eng.attrib['initWt'] = "%0.1f" % (engine.m_init * 1000.0)  # to g
        eng.attrib['propWt'] = "%0.1f" % (engine.m_prop * 1000.0)  # to g
        eng.attrib['massFrac'] = "%0.0f" % engine.m_frac

        # TODO: Needs adding
        eng.attrib['exitDia'] = "%0.2f" % 0
        eng.attrib['throatDia'] = "0."
        eng.attrib['Type'] = "single-use"
        eng.attrib['delays'] = "2,4,6,8"
        eng.attrib['auto-calc-cg'] = "1"
        eng.attrib['auto-calc-mass'] = "1"
        eng.attrib['tDiv'] = "10"
        eng.attrib['tFix'] = "1"
        eng.attrib['tStep'] = "-1."
        eng.attrib['FDiv'] = "10"
        eng.attrib['FFix'] = "1"
        eng.attrib['FStep'] = "-1."
        eng.attrib['cgDiv'] = "10"
        eng.attrib['cgFix'] = "1"
        eng.attrib['cgStep'] = "-1."
        eng.attrib['mDiv'] = "10"
        eng.attrib['mFix'] = "1"
        eng.attrib['mStep'] = "-1."

        comments = ET.SubElement(eng, 'comments')
        comments.text = engine.comments

        data = ET.SubElement(eng, 'data')

        for element in engine.make_thrustcurve():
            eng_data = ET.SubElement(data, 'eng-data')
            eng_data.attrib['t'] = "%0.5f" % element['t']
            eng_data.attrib['f'] = "%0.5f" % element['thrust']

        # pretty print
        xmldoc = minidom.parseString(ET.tostring(doc, encoding="UTF-8"))
        return xmldoc.toprettyxml(indent="  ")
