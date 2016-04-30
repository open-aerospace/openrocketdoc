#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_document
----------------------------------

Tests for `document` module.
"""

import unittest
from openrocketdoc import document


class TestOpenrocketdoc(unittest.TestCase):

    def setUp(self):
        pass

    def test_spec_a_rocket(self):
        rocket = document.Rocket("Rocket")
        stage0 = document.Stage("Booster")
        stage0.components = [
            document.Nosecone(document.Noseshape.VONKARMAN),
            document.Bodytube("body"),
        ]
        rocket.stages = [stage0]

    def test_stage_mass_sum(self):
        stage0 = document.Stage("Booster")
        stage0.components = [
            document.Nosecone(document.Noseshape.CONE, mass=0.7),
            document.Bodytube("body"),
            document.Bodytube("body", mass=24.1),
        ]
        self.assertEqual(24.8, stage0.mass)

    def test_rocket_mass_sum(self):
        stage0 = document.Stage("Booster")
        stage0.components = [
            document.Nosecone("", mass=0.7),
            document.Bodytube("body"),
            document.Bodytube("body", mass=24.1),
        ]
        stage1 = document.Stage("Booster")
        stage1.components = [
            document.Bodytube("body", mass=4.87),
            document.Fin('fin', mass=0.1),
        ]

        rocket = document.Rocket("Rocket")
        rocket.stages = [stage0, stage1]

        self.assertEqual(29.77, rocket.mass)

    def test_fins(self):
        fin = document.Fin('fin')
        self.assertEqual(0, fin.mass)

    def test_engine_length(self):
        engine = document.Engine("test")

        # length not set
        self.assertEqual(engine.length, 0)

        # set directly
        engine.length = 25.4
        self.assertEqual(engine.length, 25.4)

    def test_engine_name(self):
        engine = document.Engine("test Name")
        self.assertEqual(engine.name, "test Name")
        self.assertEqual(engine.manufacturer, "")

        engine.manufacturer = "python"
        self.assertEqual(engine.manufacturer, "python")

    def test_engine_isp(self):
        engine = document.Engine("test Name")

        self.assertEqual(engine.Isp, 0)

        engine.Isp = 169
        self.assertAlmostEqual(engine.Isp, 169)

    def test_engine_Itot(self):
        engine = document.Engine("test Name")

        self.assertEqual(engine.I_total, 0)

        engine.thrustcurve.append({'t': 0, 'thrust': 500})
        engine.thrustcurve.append({'t': 1, 'thrust': 500})

        self.assertAlmostEqual(engine.I_total, 500)

    def test_engine_avgthrust(self):
        engine = document.Engine("test Name")

        self.assertEqual(engine.thrust_avg, 0)

        engine.thrustcurve.append({'t': 0, 'thrust': 500})
        engine.thrustcurve.append({'t': 1, 'thrust': 500})

        self.assertAlmostEqual(engine.thrust_avg, 500)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
