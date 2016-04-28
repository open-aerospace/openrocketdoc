# -*- coding: utf-8 -*-

from __future__ import print_function


class RaspEngine(object):
    """Write a RASP engine file format
    """

    def __init__(self):
        pass

    def dump(self, engine):

        # comments
        doc = ";"
        doc = engine.comments.replace('\n', "\n;")
        doc += '\n'
        # header
        doc += ' '.join([
            engine.name,
            "%0.0f" % (engine.diameter * 1000),
            "%0.0f" % (engine.length * 1000),
            "0",
            "%0.4f" % (engine.m_prop),
            "%0.4f" % (engine.m_init),
            engine.manufacturer,
        ])
        doc += '\n'

        for element in engine.thrustcurve:
            doc += "%0.3f %0.3f\n" % (element['t'], element['thrust'])

        return doc
