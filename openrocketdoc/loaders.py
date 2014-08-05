#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import openrocketdoc as rdoc


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
                    component['data'] = rdoc.Nosecone()
                    for desc in subcomponent:
                        if desc.tag == 'name':
                            component['data'].name = desc.text
                        if desc.tag == 'length':
                            component['data'].length = float(desc.text)
                        if desc.tag == 'shape':
                            component['data'].shape = desc.text
                        if desc.tag == 'thickness':
                            component['data'].thickness = desc.text

                component['data'] = component.get('data', rdoc.Component()).__dict__
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
