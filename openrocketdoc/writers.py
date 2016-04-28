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
