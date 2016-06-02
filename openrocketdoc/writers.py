# -*- coding: utf-8 -*-

from __future__ import print_function
from openrocketdoc import document as rdoc
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from yaml import dump as yamldump

N2LBF = 0.224809
KG2LB = 2.20462


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

        # All components have optional tags
        c['tags'] = component.tags

        # Type specific writers:
        if type(component) is rdoc.Nosecone:
            c['shape'] = component.shape.name
            c['shape_parameter'] = component.shape_parameter
            c['thickness'] = component.thickness
            c['surface'] = component.surface_roughness
            c['mass'] = component.component_mass
            c['length'] = component.length
            c['diameter'] = component.diameter
            if component.color:
                c['color'] = '['+str(component.color[0])+','+str(component.color[1])+','+str(component.color[2])+']'

        elif type(component) is rdoc.Bodytube:
            c['mass'] = component.component_mass
            c['length'] = component.length
            c['diameter'] = component.diameter
            c['surface'] = component.surface_roughness
            c['thickness'] = component.thickness
            if component.color:
                c['color'] = '['+str(component.color[0])+','+str(component.color[1])+','+str(component.color[2])+']'

        elif type(component) is rdoc.Finset:
            c['fin'] = self._component_dict(component.components[0])
            c['num_of_fins'] = len(component.components)

        elif type(component) is rdoc.Fin:
            c['root_chord'] = component.root
            c['tip_chord'] = component.tip
            c['span'] = component.span
            c['sweepangle'] = component.sweepangle
            c['mass'] = component.component_mass

        # recursion
        # However, a finset describes one fin only, no need to list them redundantly
        if component.components and type(component) is not rdoc.Finset:
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


class SVG(object):
    """Draw an representation of a rocket as an SVG document

    **Members:**
    """

    @classmethod
    def dump(cls, ordoc):
        """Return a `str` entire svg drawing of the rocket

        :param ordoc: the OpenRocketDoc file to convert
        :returns: `str` formated file
        """

        # SVG header
        svg = ET.Element('svg')
        svg.attrib['xmlns:dc'] = "http://purl.org/dc/elements/1.1/"
        svg.attrib['xmlns:cc'] = "http://creativecommons.org/ns#"
        svg.attrib['xmlns:rdf'] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        svg.attrib['xmlns:svg'] = "http://www.w3.org/2000/svg"
        svg.attrib['xmlns'] = "http://www.w3.org/2000/svg"
        svg.attrib['version'] = "1.1"
        svg.attrib['id'] = "svg2"

        # Landscape A4 paper
        svg.attrib['viewBox'] = "0 0 1052.3622047 744.09448819 "
        svg.attrib['height'] = "210mm"
        svg.attrib['width'] = "297mm"

        # Group to draw in
        drawing = ET.SubElement(svg, 'g')
        drawing.attrib['id'] = "rocket"

        position = 0
        # Draw elements:
        for component in ordoc.stages[0].components:

            if type(component) == rdoc.Nosecone:
                path = ET.SubElement(drawing, 'path')
                path.attrib['id'] = "nose"

                points = []
                points.append((component.length, component.diameter / 2.0))
                points.append((0, 0))
                points.append((component.length, -component.diameter / 2.0))

                path.attrib['d'] = "M " + " ".join(["%0.5f,%0.5f" % (p[0], p[1]) for p in points])
                path.attrib['style'] = "fill:none;stroke:#000000;stroke-width:0.001px;"
                position += component.length

            if type(component) == rdoc.Bodytube:
                path = ET.SubElement(drawing, 'rect')
                path.attrib['id'] = component.name
                path.attrib['x'] = "%0.4f" % position
                path.attrib['y'] = "%0.4f" % (-component.diameter / 2.0)
                path.attrib['width'] = "%0.4f" % component.length
                path.attrib['height'] = "%0.4f" % component.diameter
                path.attrib['style'] = "fill:none;stroke:#000000;stroke-width:0.001px;"
                position += component.length

        scale = 900 / position
        drawing.attrib['transform'] = "translate(75,372) scale(%0.1f,%0.1f)" % (scale, scale)

        # pretty print
        xmldoc = minidom.parseString(ET.tostring(svg, encoding="UTF-8"))
        return xmldoc.toprettyxml(indent="  ")


class JSBSimAircraft(object):
    """JSBSim Aircraft format

    **Members:**
    """

    @classmethod
    def dump(cls, ordoc):
        """Return a `str` representation of the file.

        :param ordoc: The OpenRocketDoc file to convert
        :returns: `str` formated file
        """

        doc = ET.Element('fdm_config')
        doc.attrib['name'] = ordoc.name
        doc.attrib['version'] = "2.0"
        doc.attrib['xmlns:xsi'] = "http://www.w3.org/2001/XMLSchema-instance"
        doc.attrib['xsi:noNamespaceSchemaLocation'] = "http://jsbsim.sourceforge.net/JSBSim.xsd"
        doc.attrib['release'] = "ALPHA"

        ET.SubElement(doc, 'fileheader')

        doc.append(ET.Comment("\n  Primary Metrics (Size of vehicle)\n  "))

        # METRICS
        #######################################################################
        metrics = ET.SubElement(doc, 'metrics')
        wingarea = ET.SubElement(metrics, 'wingarea')
        wingarea.attrib['unit'] = "M2"
        wingarea.text = "0.0"

        wingspan = ET.SubElement(metrics, 'wingspan')
        wingspan.attrib['unit'] = "M"
        wingspan.text = "0.0"

        chord = ET.SubElement(metrics, 'chord')
        chord.attrib['unit'] = "M"
        chord.text = "0.0"

        htailarea = ET.SubElement(metrics, 'htailarea')
        htailarea.attrib['unit'] = "M2"
        htailarea.text = "0.0"

        htailarm = ET.SubElement(metrics, 'htailarm')
        htailarm.attrib['unit'] = "M"
        htailarm.text = "0.0"

        vtailarea = ET.SubElement(metrics, 'vtailarea')
        vtailarea.attrib['unit'] = "M2"
        vtailarea.text = "0.0"

        vtailarm = ET.SubElement(metrics, 'vtailarm')
        vtailarm.attrib['unit'] = "M"
        vtailarm.text = "0.0"

        location_cp = ET.SubElement(metrics, 'location')
        location_cp.attrib['name'] = "AERORP"
        location_cp.attrib['unit'] = "M"
        ET.SubElement(location_cp, 'x').text = "0.0"
        ET.SubElement(location_cp, 'y').text = "0.0"
        ET.SubElement(location_cp, 'z').text = "0.0"

        doc.append(ET.Comment("\n  Mass Elements: describe dry mass of vehicle\n  "))

        # MASS BALANCE
        #######################################################################
        mass_balance = ET.SubElement(doc, 'mass_balance')

        position = 0
        for component in ordoc.stages[0].components:
            if type(component) == rdoc.Bodytube:

                # New pointmass
                pointmass = ET.SubElement(mass_balance, 'pointmass')
                pointmass.attrib['name'] = component.name

                # Has a Form
                form = ET.SubElement(pointmass, 'form')
                form.attrib['shape'] = "tube"
                radius = ET.SubElement(form, 'radius')
                radius.attrib['unit'] = "M"
                radius.text = "%0.4f" % (component.diameter/2.0)
                length = ET.SubElement(form, 'length')
                length.attrib['unit'] = "M"
                length.text = "%0.4f" % component.length

                # And a Mass
                weight = ET.SubElement(pointmass, 'weight')
                weight.attrib['unit'] = "KG"
                weight.text = "%0.4f" % component.component_mass

                # And a Location
                location = ET.SubElement(pointmass, 'location')
                location.attrib['unit'] = "M"
                ET.SubElement(location, 'x').text = "%0.4f" % (position + (component.length/2.0))
                ET.SubElement(location, 'y').text = "0.0"
                ET.SubElement(location, 'z').text = "0.0"

                # What about stuff in this component
                for subcomponent in component.components:
                    if type(subcomponent) == rdoc.Mass:
                        pointmass = ET.SubElement(mass_balance, 'pointmass')

            # Keep running tabs on the distance from nosecone
            position += component.length

        doc.append(ET.Comment("\n  Propulsion: describe tanks, fuel and link to engine def files\n  "))

        # PROPULSION
        #######################################################################
        prop = ET.SubElement(doc, 'propulsion')
        for component in ordoc.stages[0].components:
            for subc in component.components:
                if type(subc) == rdoc.Engine:

                    tank = ET.SubElement(prop, 'tank')
                    tank.attrib['type'] = "FUEL"
                    location = ET.SubElement(tank, 'location')
                    location.attrib['unit'] = "M"
                    ET.SubElement(location, 'x').text = "0.0"
                    ET.SubElement(location, 'y').text = "0.0"
                    ET.SubElement(location, 'z').text = "0.0"
                    radius = ET.SubElement(tank, 'radius')
                    radius.attrib['unit'] = "M"
                    radius.text = "0"
                    grain_config = ET.SubElement(tank, 'grain_config')
                    grain_config.attrib['type'] = "CYLINDRICAL"
                    grain_length = ET.SubElement(grain_config, 'length')
                    grain_length.attrib['unit'] = "M"
                    grain_length.text = "0"
                    grain_dia = ET.SubElement(grain_config, 'bore_diameter')
                    grain_dia.attrib['unit'] = "M"
                    grain_dia.text = "0"
                    capacity = ET.SubElement(tank, 'capacity')
                    capacity.attrib['unit'] = "KG"
                    capacity.text = "0"
                    contents = ET.SubElement(tank, 'contents')
                    contents.attrib['unit'] = "KG"
                    contents.text = "0"

                    eng = ET.SubElement(prop, 'engine')
                    eng.attrib['file'] = subc.name
                    ET.SubElement(eng, 'feed').text = "0"
                    eng_loc = ET.SubElement(eng, 'location')
                    eng_loc.attrib['unit'] = "M"
                    ET.SubElement(eng_loc, 'x').text = "0.0"
                    ET.SubElement(eng_loc, 'y').text = "0.0"
                    ET.SubElement(eng_loc, 'z').text = "0.0"
                    thruster = ET.SubElement(eng, 'thruster')
                    thruster.attrib['file'] = subc.name
                    thrust_loc = ET.SubElement(thruster, 'location')
                    thrust_loc.attrib['unit'] = "M"

                    ET.SubElement(thrust_loc, 'x').text = "0.0"
                    ET.SubElement(thrust_loc, 'y').text = "0.0"
                    ET.SubElement(thrust_loc, 'z').text = "0.0"

        # AERODYNAMICS
        #######################################################################
        ET.SubElement(doc, 'aerodynamics')

        # ground_reactions
        #######################################################################
        ET.SubElement(doc, 'ground_reactions')

        # SYSTEM
        #######################################################################
        ET.SubElement(doc, 'system')

        # pretty print
        xmldoc = minidom.parseString(ET.tostring(doc, encoding="UTF-8"))
        return xmldoc.toprettyxml(indent="  ")


class JSBSimEngine(object):
    """JSBSim Engine format

    **Memebers:**
    """

    @classmethod
    def dump(cls, engine):
        """Return a `str` representation of the file.

        :param `Engine` engine: The OpenRocketDoc engine to convert
        :returns: `str` formated file
        """

        doc = ET.Element('rocket_engine')
        doc.attrib['name'] = engine.name

        isp = ET.SubElement(doc, 'isp')
        isp.text = "%0.1f" % engine.Isp

        # TODO: What to do about motor build-up time?
        builduptime = ET.SubElement(doc, 'builduptime')
        builduptime.text = "0.1"

        thrust_table = ET.SubElement(doc, 'thrust_table')
        thrust_table.attrib['name'] = "propulsion/thrust_prop_remain"  # apparently the only option?
        thrust_table.attrib['type'] = "internal"

        tableData = ET.SubElement(thrust_table, 'tableData')
        tableData.text = "\n"

        if not engine.thrustcurve:
            thrustcurve = engine.make_thrustcurve()
        else:
            thrustcurve = engine.thrustcurve

        # First data point is at t=0, 0 prop burnt
        tableData.text += "      %0.3f %0.3f\n" % (0.0, thrustcurve[0]['thrust'] * N2LBF)

        # Compute propellent burn, _first_ result will be at t = i+1
        itot = 0
        for i, t in enumerate(thrustcurve[:-1]):
            x = t['t']
            x_1 = thrustcurve[i+1]['t']
            f_x = t['thrust']
            f_x1 = thrustcurve[i+1]['thrust']
            itot += (x_1 - x) * (f_x1 + f_x)

            mass = ((itot/2.0)/engine.V_e) * KG2LB
            thrust = f_x1 * N2LBF

            tableData.text += "      %0.3f %0.3f\n" % (mass, thrust)

        tableData.text += "    "

        # pretty print
        xmldoc = minidom.parseString(ET.tostring(doc, encoding="UTF-8"))
        return xmldoc.toprettyxml(indent="  ")


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

        # TODO: These all need adding tp the doc:
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
