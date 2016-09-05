# -*- coding: utf-8 -*-

from __future__ import print_function
from openrocketdoc import document as rdoc
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from yaml import dump as yamldump
from math import pi

# Unit conversions
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
        if component.tags:
            c['tags'] = component.tags

        if type(component) is rdoc.Nosecone:
            c['shape'] = component.shape.name
            c['shape_parameter'] = component.shape_parameter
            if component.thickness > 0:
                c['thickness'] = component.thickness
            if component.surface_roughness > 0:
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
            if component.thickness > 0:
                c['thickness'] = component.thickness
            if component.surface_roughness > 0:
                c['surface'] = component.surface_roughness
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
            if ordoc.description:
                doc['rocket']['description'] = ordoc.description
            if ordoc.manufacturer:
                doc['rocket']['manufacturer'] = ordoc.manufacturer
            doc['rocket']['aerodynamics'] = ordoc.aero_properties

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

    MM2PX = 11.81  # 300 dpi

    @classmethod
    def _draw_scale(cls, doc, scalefactor):

        # local convenience function to get units in px.
        def scale(u):
            mm = u * scalefactor * 1000
            px = mm * cls.MM2PX
            return px

        if scalefactor >= 0.5:
            unit = 1.0
            unit_name = "1 m"
        elif scalefactor < 0.5:
            unit = 0.1
            unit_name = "10 cm"

        scalebar = ET.SubElement(doc, 'g')
        scalebar.attrib['id'] = "scalebar"

        line = ET.SubElement(scalebar, 'path')
        line.attrib['d'] = "M " + " ".join(["%0.5f,%0.5f" % (scale(p[0]), scale(p[1])) for p in [(0, 0), (unit, 0)]])
        line.attrib['style'] = "fill:none;stroke:#000000;stroke-width:5px;"

        zero = ET.SubElement(scalebar, 'text')
        zero.attrib['x'] = "0"
        zero.attrib['y'] = "65"
        zero.attrib['style'] = "font-style:normal;font-weight:normal;font-size:60px;font-family:sans-serif;fill:#000000;fill-opacity:1;stroke:none;"
        ET.SubElement(zero, 'tspan').text = "0"

        one = ET.SubElement(scalebar, 'text')
        one.attrib['x'] = "%0.5f" % scale(unit)
        one.attrib['y'] = "65"
        one.attrib['style'] = "font-style:normal;font-weight:normal;font-size:60px;font-family:sans-serif;fill:#000000;fill-opacity:1;stroke:none;"
        ET.SubElement(one, 'tspan').text = unit_name

        scalebar.attrib['transform'] = "translate(350,2200)"

    @classmethod
    def _draw_border(cls, doc):
        border = ET.SubElement(doc, 'g')
        border.attrib['id'] = "border"

        box = ET.SubElement(border, 'rect')
        box.attrib['x'] = "50"
        box.attrib['y'] = "50"
        box.attrib['width'] = "3400"
        box.attrib['height'] = "2350"
        box.attrib['style'] = "fill:none;stroke:#999999;stroke-width:2px;"

        for i, n in enumerate(["4", "3", "2", "1"]):
            num = ET.SubElement(border, 'text')
            num.attrib['x'] = "4"
            num.attrib['y'] = "%0.5f" % (360 + i * 587)
            num.attrib['style'] = "font-style:normal;font-weight:normal;font-size:60px;font-family:sans-serif;fill:#999999;fill-opacity:1;stroke:none;"
            num.attrib['transform'] = "rotate(-90, 45, %0.5f)" % (360 + i * 587)
            ET.SubElement(num, 'tspan').text = n

            num = ET.SubElement(border, 'text')
            num.attrib['x'] = "3455"
            num.attrib['y'] = "%0.5f" % (366 + i * 587)
            num.attrib['style'] = "font-style:normal;font-weight:normal;font-size:60px;font-family:sans-serif;fill:#999999;fill-opacity:1;stroke:none;"
            ET.SubElement(num, 'tspan').text = n

            if i > 2:
                continue
            line = ET.SubElement(border, 'path')
            line.attrib['d'] = "M 0,{h} 50,{h}".format(h=(690 + i * 587))
            line.attrib['style'] = "fill:none;stroke:#999999;stroke-width:2px;"
            line = ET.SubElement(border, 'path')
            line.attrib['d'] = "M 3450,{h} 3500,{h}".format(h=(690 + i * 587))
            line.attrib['style'] = "fill:none;stroke:#999999;stroke-width:2px;"

    @classmethod
    def dump(cls, ordoc, drawscale=True, drawborder=True):
        """Return a `str` entire svg drawing of the rocket

        :param ordoc: the OpenRocketDoc file to convert
        :param bool drawscale: (optional) if true, draws a scale bar in the document.
        :param bool drawborder: (optional) if true, draws an engineering border around the document.
        :returns: `str` SVG document
        """

        # Determine the scale:
        length = ordoc.length
        scalefactor = 0.230 / (length + 0.001)  # avoid divide by 0

        # local convenience function to get units in px.
        def scale(u):
            mm = u * scalefactor * 1000
            px = mm * cls.MM2PX
            return px

        # SVG header
        svg = ET.Element('svg')
        svg.attrib['xmlns:dc'] = "http://purl.org/dc/elements/1.1/"
        svg.attrib['xmlns:rdf'] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        svg.attrib['xmlns:svg'] = "http://www.w3.org/2000/svg"
        svg.attrib['xmlns'] = "http://www.w3.org/2000/svg"
        svg.attrib['version'] = "1.1"
        svg.attrib['id'] = "svg2"

        # Landscape A4 paper
        svg.attrib['viewBox'] = "0 0 3508 2480"  # 2480 x 3508 pixels (210mm X 297mm @ 300 dpi)
        svg.attrib['height'] = "210mm"
        svg.attrib['width'] = "297mm"

        if drawborder:
            cls._draw_border(svg)

        # Group to draw in
        drawing = ET.SubElement(svg, 'g')
        drawing.attrib['id'] = "rocket"

        position = 0
        # Draw elements:
        for component in ordoc.stages[0].components:

            # Nosecone ########################################################
            if type(component) == rdoc.Nosecone:
                path = ET.SubElement(drawing, 'path')
                path.attrib['id'] = "nose"

                points = []
                points.append((component.length, component.diameter / 2.0))
                points.append((0, 0))
                points.append((component.length, -component.diameter / 2.0))

                path.attrib['d'] = "M " + " ".join(["%0.5f,%0.5f" % (scale(p[0]), scale(p[1])) for p in points])
                path.attrib['style'] = "fill:none;stroke:#666666;stroke-width:4px;"
                position += component.length

            # Bodytube ########################################################
            if type(component) == rdoc.Bodytube:
                path = ET.SubElement(drawing, 'rect')
                path.attrib['id'] = component.name
                path.attrib['x'] = "%0.4f" % scale(position)
                path.attrib['y'] = "%0.4f" % scale(-component.diameter / 2.0)
                path.attrib['width'] = "%0.4f" % scale(component.length)
                path.attrib['height'] = "%0.4f" % scale(component.diameter)
                path.attrib['style'] = "fill:none;stroke:#666666;stroke-width:4px;"
                position += component.length

                path = ET.SubElement(drawing, 'circle')
                path.attrib['cx'] = "800"
                path.attrib['cy'] = "800"
                path.attrib['r'] = "%0.5f" % scale(component.diameter / 2.0)
                path.attrib['style'] = "fill:none;stroke:#666666;stroke-width:4px;"

                path = ET.SubElement(drawing, 'circle')
                path.attrib['cx'] = "800"
                path.attrib['cy'] = "800"
                path.attrib['r'] = "2"
                path.attrib['style'] = "fill:none;stroke:#666666;stroke-width:4px;"


        drawing.attrib['transform'] = "translate(350,700)"

        if drawscale:
            cls._draw_scale(svg, scalefactor)

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

        # METRICS
        #######################################################################
        doc.append(ET.Comment("\n\n  Primary Metrics (Ovearall size of vehicle)\n\n  "))

        metrics = ET.SubElement(doc, 'metrics')
        wingarea = ET.SubElement(metrics, 'wingarea')
        wingarea.attrib['unit'] = "M2"

        # Wing area is either something you know (e.g: using wind tunnel data)
        # Or it's the cross sectional area of the rocket (area of a circle the
        # diameter of the rocket)
        if ordoc.aero_properties.get('area'):
            wingarea.text = "%f" % ordoc.aero_properties.get('area')
        else:
            wingarea.text = "%0.4f" % (pi * (ordoc.diameter / 2.0)**2)

        wingspan = ET.SubElement(metrics, 'wingspan')
        wingspan.attrib['unit'] = "M"

        # Wing span is either something you know (e.g: using wind tunnel data)
        # Or it's the diameter of the rocket (usually treated as the
        # characteristic length)
        wingspan.text = "0.0"
        if ordoc.aero_properties.get('span'):
            wingspan.text = "%f" % ordoc.aero_properties.get('span')
        else:
            wingspan.text = "%0.4f" % ordoc.diameter

        # I don't know what this does
        chord = ET.SubElement(metrics, 'chord')
        chord.attrib['unit'] = "M"
        chord.text = "0.0"

        # I don't know what this does
        htailarea = ET.SubElement(metrics, 'htailarea')
        htailarea.attrib['unit'] = "M2"
        htailarea.text = "0.0"

        # I don't know what this does
        htailarm = ET.SubElement(metrics, 'htailarm')
        htailarm.attrib['unit'] = "M"
        htailarm.text = "0.0"

        # I don't know what this does
        vtailarea = ET.SubElement(metrics, 'vtailarea')
        vtailarea.attrib['unit'] = "M2"
        vtailarea.text = "0.0"

        # I don't know what this does
        vtailarm = ET.SubElement(metrics, 'vtailarm')
        vtailarm.attrib['unit'] = "M"
        vtailarm.text = "0.0"

        location_cp = ET.SubElement(metrics, 'location')
        location_cp.attrib['name'] = "AERORP"
        location_cp.attrib['unit'] = "M"

        # If we don't know the center of pressure, just put it at the back of
        # the rocket so it's stable.
        if ordoc.aero_properties.get('area'):
            ET.SubElement(location_cp, 'x').text = "%f" % ordoc.aero_properties.get('CP')[0]
        else:
            ET.SubElement(location_cp, 'x').text = "%0.4f" % ordoc.length

        ET.SubElement(location_cp, 'y').text = "0.0"
        ET.SubElement(location_cp, 'z').text = "0.0"

        # MASS BALANCE
        #######################################################################
        doc.append(ET.Comment("\n\n  Mass Elements: describe dry mass of vehicle\n\n  "))

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

        doc.append(ET.Comment("\n\n  Propulsion: describe tanks, fuel and link to engine def files\n\n  "))

        # PROPULSION
        #######################################################################
        prop = ET.SubElement(doc, 'propulsion')
        position = 0
        for component in ordoc.stages[0].components:
            for subc in component.components:
                if type(subc) == rdoc.Engine:
                    engine = subc

                    tank = ET.SubElement(prop, 'tank')
                    tank.attrib['type'] = "FUEL"
                    location = ET.SubElement(tank, 'location')
                    location.attrib['unit'] = "M"
                    ET.SubElement(location, 'x').text = "%0.4f" % (position + (engine.length / 2.0))
                    ET.SubElement(location, 'y').text = "0.0"
                    ET.SubElement(location, 'z').text = "0.0"
                    radius = ET.SubElement(tank, 'radius')
                    radius.attrib['unit'] = "M"
                    radius.text = "%0.4f" % (engine.diameter / 2.0)
                    grain_config = ET.SubElement(tank, 'grain_config')
                    grain_config.attrib['type'] = "CYLINDRICAL"
                    grain_length = ET.SubElement(grain_config, 'length')
                    grain_length.attrib['unit'] = "M"
                    grain_length.text = "%0.4f" % engine.length
                    grain_dia = ET.SubElement(grain_config, 'bore_diameter')
                    grain_dia.attrib['unit'] = "M"
                    grain_dia.text = "0"
                    capacity = ET.SubElement(tank, 'capacity')
                    capacity.attrib['unit'] = "KG"
                    capacity.text = "%0.4f" % engine.m_prop
                    contents = ET.SubElement(tank, 'contents')
                    contents.attrib['unit'] = "KG"
                    contents.text = "%0.4f" % engine.m_prop

                    eng = ET.SubElement(prop, 'engine')
                    eng.attrib['file'] = engine.name_slug
                    ET.SubElement(eng, 'feed').text = "0"
                    eng_loc = ET.SubElement(eng, 'location')
                    eng_loc.attrib['unit'] = "M"
                    ET.SubElement(eng_loc, 'x').text = "%0.4f" % position
                    ET.SubElement(eng_loc, 'y').text = "0.0"
                    ET.SubElement(eng_loc, 'z').text = "0.0"
                    thruster = ET.SubElement(eng, 'thruster')
                    thruster.attrib['file'] = engine.name_slug + "_nozzle"
                    thrust_loc = ET.SubElement(thruster, 'location')
                    thrust_loc.attrib['unit'] = "M"
                    ET.SubElement(thrust_loc, 'x').text = "%0.4f" % (position + engine.length)
                    ET.SubElement(thrust_loc, 'y').text = "0.0"
                    ET.SubElement(thrust_loc, 'z').text = "0.0"

            # after we finish reading subcomponents, set position
            position += component.length

        # AERODYNAMICS
        #######################################################################
        doc.append(ET.Comment("\n\n  Aerodynamics\n\n  "))
        aero = ET.SubElement(doc, 'aerodynamics')

        # Drag
        drag_table = ordoc.aero_properties.get('CD', [])
        if drag_table:
            drag_axis = ET.SubElement(aero, 'axis')
            drag_axis.attrib['name'] = "DRAG"

            drag_function = ET.SubElement(drag_axis, 'function')
            drag_function.attrib['name'] = "aero/force/drag"
            ET.SubElement(drag_function, 'description').text = "Coefficient of Drag"

            drag_prod = ET.SubElement(drag_function, 'product')
            ET.SubElement(drag_prod, 'property').text = "aero/qbar-psf"
            ET.SubElement(drag_prod, 'property').text = "metrics/Sw-sqft"

            if len(drag_table) > 1:
                drag_tab = ET.SubElement(drag_prod, 'table')
                drag_tab.attrib['name'] = "aero/coefficient/CD_min"
                ET.SubElement(drag_tab, 'independentVar').text = "velocities/mach"
                drag_tabledata = ET.SubElement(drag_tab, 'tableData')
                drag_tabledata.text = "\n"
                for entry in drag_table:
                    drag_tabledata.text += "%20.4f  %0.5f\n" % (entry[0], entry[1])
                drag_tabledata.text += "            "
            else:
                ET.SubElement(drag_prod, 'value').text = "%f" % drag_table[0]

        doc.append(ET.Comment("\n  Ground reactions and systems are not auto-generated.\n  "))

        ET.SubElement(doc, 'ground_reactions')
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
