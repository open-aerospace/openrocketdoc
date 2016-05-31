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
            document.Nosecone(document.Noseshape.VONKARMAN, 1, 0.7, 1.2),
            document.Bodytube("body", 1.2, 0.5),
        ]
        rocket.stages = [stage0]

    def test_stage_mass_sum(self):
        stage0 = document.Stage("Booster")
        stage0.components = [
            document.Nosecone(document.Noseshape.CONE, 0, 0.7, 1.4),
            document.Bodytube("body", 0, 1),
            document.Bodytube("body", 24.1, 1),
        ]
        self.assertEqual(24.8, stage0.mass)

    def test_rocket_mass_sum(self):
        stage0 = document.Stage("Booster")
        stage0.components = [
            document.Nosecone("", 1, 0.7, 1.2),
            document.Bodytube("body", 0, 1),
            document.Bodytube("body", 24.1, 1),
        ]
        stage1 = document.Stage("Booster")
        stage1.components = [
            document.Bodytube("body", 4.87, 1),
            document.Fin('fin', 1, 1, 1, sweepangle=45.0, mass=0.1),
        ]

        rocket = document.Rocket("Rocket")
        rocket.stages = [stage0, stage1]

        self.assertEqual(29.77, rocket.mass)

    def test_fins(self):
        fin = document.Fin('fin', 1, 1, 1, sweep=0.234)
        self.assertEqual(0, fin.mass)
        self.assertAlmostEqual(fin.root, 1.0)
        self.assertAlmostEqual(fin.tip, 1.0)
        self.assertAlmostEqual(fin.span, 1.0)
        self.assertAlmostEqual(fin.sweep, 0.234)
        self.assertAlmostEqual(fin.sweepangle, 13.170241897951414)

    def test_no_color(self):
        tube = document.Bodytube("body", 24.1, 1)

        # No color defined
        self.assertEqual(tube.color, None)

    def test_color(self):
        tube = document.Bodytube("body", 24.1, 1)

        # As string:
        tube.color = "Brown"
        self.assertEqual(tube.color, "Brown")

        # As tuple:
        tube.color = (240, 12, 0)
        self.assertEqual(tube.color, (240, 12, 0))

    def test_engine_length(self):
        engine = document.Engine("test")

        # length not set
        self.assertEqual(engine.length, 0)

        # set directly
        engine.length = 25.4
        self.assertEqual(engine.length, 25.4)

    def test_engine_t_burn(self):
        engine = document.Engine("test Name")
        engine.t_burn = 123.456
        self.assertAlmostEqual(engine.t_burn, 123.456)

    def test_engine_ve(self):
        engine = document.Engine("test Name")
        engine.Isp = 123
        self.assertAlmostEqual(engine.V_e, 1206.21795)

    def test_engine_simple_0(self):
        engine = document.Engine("test Name")

        # minimum to set up real engine
        engine.Isp = 123
        engine.thrust_avg = 4567
        engine.t_burn = 89

        self.assertAlmostEqual(engine.Isp, 123)
        self.assertAlmostEqual(engine.thrust_avg, 4567)
        self.assertAlmostEqual(engine.t_burn, 89)

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
