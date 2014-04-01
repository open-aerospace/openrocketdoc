#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from zipfile import ZipFile
import xml.etree.ElementTree as ET

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
                for rocket in base:
                    if rocket.tag == 'name':
                        rocket_name = rocket.text
                    if rocket.tag == 'subcomponents':
                        for stage in rocket:
                            if stage.tag == 'stage':
                                for stageinfo in stage:
                                    if stageinfo.tag == 'name':
                                        stage = {'name': stageinfo.text}
                                    for comp in stageinfo:
                                        print (comp.tag, comp.attrib)
                            stages.append(stage)

        self.rocket = {'name': rocket_name, 'stages': stages}
