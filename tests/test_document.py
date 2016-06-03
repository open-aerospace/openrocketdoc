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

    def test_rocket_aero_exist(self):
        rocket = document.Rocket("Rocket")
        self.assertEqual(rocket.aero_properties, {})

        # add some properties
        rocket.aero_properties['CD'] = [0.8]
        self.assertEqual(rocket.aero_properties, {'CD': [0.8]})

    def test_rocket_length_sum_0(self):
        # just rocket
        rocket = document.Rocket("Rocket")
        self.assertEqual(rocket.length, 0)

        # rocket and a stage
        stage0 = document.Stage("sustainer")
        rocket.stages = [stage0]
        self.assertEqual(rocket.length, 0)

        # zero length components in rocket
        stage0.components = [
            document.Nosecone("", 1, 0.7, 0),
            document.Bodytube("body", 0, 0),
            document.Bodytube("body", 24.1, 0)
        ]
        self.assertEqual(rocket.length, 0)

    def test_rocket_length_sum(self):
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

        self.assertAlmostEqual(rocket.length, 5.2)

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
        self.assertAlmostEqual(engine.m_prop, 336.9730984354)
        self.assertAlmostEqual(engine.I_total, 406463)
        self.assertAlmostEqual(engine.thrust_peak, 4567)
        self.assertAlmostEqual(engine.V_e, 1206.21795)

    def test_engine_simple_1(self):
        engine = document.Engine("test Name")

        # minimum to set up real engine
        engine.Isp = 123
        engine.thrust_avg = 4567
        engine.I_total = 15000

        self.assertAlmostEqual(engine.Isp, 123)
        self.assertAlmostEqual(engine.thrust_avg, 4567)
        self.assertAlmostEqual(engine.I_total, 15000)
        self.assertAlmostEqual(engine.m_prop, 12.435563572901)
        self.assertAlmostEqual(engine.t_burn, 3.2844317932997593)
        self.assertAlmostEqual(engine.thrust_peak, 4567)
        self.assertAlmostEqual(engine.V_e, 1206.21795)

    def test_engine_name(self):
        engine = document.Engine("test Name")
        self.assertEqual(engine.name, "test Name")
        self.assertEqual(engine.manufacturer, "")

        engine.manufacturer = "python"
        self.assertEqual(engine.manufacturer, "python")

    def test_engine_nar_code(self):
        # blank engine case
        engine = document.Engine("test Name")
        self.assertEqual(engine.nar_code, "")

        # NAR B motor spec: 2.51 –- 5.00 Ns
        # 0% B motor, it's almost zero
        engine.thrust_avg = 2.501
        engine.t_burn = 1
        self.assertEqual(engine.nar_code, "B")
        self.assertAlmostEqual(engine.nar_percent, 0, places=1)
        # 50% B motor
        engine.thrust_avg = 3.755
        engine.t_burn = 1
        self.assertEqual(engine.nar_code, "B")
        self.assertAlmostEqual(engine.nar_percent, 50, places=0)
        # 100% B motor, but it rounds up, that's okay I guess
        engine.thrust_avg = 4.99999
        engine.t_burn = 1
        self.assertEqual(engine.nar_code, "B")
        self.assertAlmostEqual(engine.nar_percent, 100, places=0)

        # NAR N motor spec: 10,200 -- 20,500 Ns
        # 0% N motor
        engine.thrust_avg = 10200
        engine.t_burn = 1
        engine.nar_percent
        self.assertEqual(engine.nar_code, "M")
        self.assertAlmostEqual(engine.nar_percent, 99, places=0)
        # 50% N motor
        engine.thrust_avg = 10240 + 5150
        engine.t_burn = 1
        self.assertEqual(engine.nar_code, "N")
        self.assertAlmostEqual(engine.nar_percent, 50, places=0)
        # 100% N motor
        engine.thrust_avg = 20450
        engine.t_burn = 1
        self.assertEqual(engine.nar_code, "N")
        self.assertAlmostEqual(engine.nar_percent, 100, places=0)

        # NAR Z motor spec: 41,900,000 -- 83,900,000 Ns
        # 0% N motor
        engine.thrust_avg = 41.9e6
        engine.t_burn = 1
        engine.nar_percent
        self.assertEqual(engine.nar_code, "Y")
        self.assertAlmostEqual(engine.nar_percent, 100, places=0)
        # 50% N motor
        engine.thrust_avg = 41.9e6 + 10e6
        engine.t_burn = 1
        self.assertEqual(engine.nar_code, "Z")
        self.assertAlmostEqual(engine.nar_percent, 24, places=0)
        # 100% N motor
        engine.thrust_avg = 83.8e6
        engine.t_burn = 1
        self.assertEqual(engine.nar_code, "Z")
        self.assertAlmostEqual(engine.nar_percent, 100, places=0)

        # Greater than Z:
        engine.thrust_avg = 500e6
        engine.t_burn = 1
        self.assertEqual(engine.nar_code, "AC")
        self.assertAlmostEqual(engine.nar_percent, 49, places=0)

    def test_engine_name_slug(self):

        # replace spaces with dashes
        engine = document.Engine("My Rocket Motor 12")
        self.assertEqual(engine.name_slug, "my-rocket-motor-12")

        # one word, not much to do
        engine = document.Engine("Motor")
        self.assertEqual(engine.name_slug, "motor")

        # trailing space
        engine = document.Engine("Motor ")
        self.assertEqual(engine.name_slug, "motor")

        # leading space
        engine = document.Engine(" Motor")
        self.assertEqual(engine.name_slug, "motor")

        # blank name
        engine = document.Engine("")
        self.assertEqual(engine.name_slug, "engine")

        # blank name
        engine = document.Engine(" ")
        self.assertEqual(engine.name_slug, "engine")

        # blank name
        engine = document.Engine("  ")
        self.assertEqual(engine.name_slug, "engine")

        # Illegal characters
        engine = document.Engine("my **engIne: ")
        self.assertEqual(engine.name_slug, "my-engine")

    def test_component_name_slug(self):

        # replace spaces with dashes
        c = document.Bodytube("My Rocket Tube", 1, 1)
        self.assertEqual(c.name_slug, "my-rocket-tube")

    def test_rocket_name_slug(self):

        # replace spaces with dashes
        c = document.Rocket("My Rocket")
        self.assertEqual(c.name_slug, "my-rocket")

    def test_stage_name_slug(self):

        # replace spaces with dashes
        c = document.Stage("Stage-0")
        self.assertEqual(c.name_slug, "stage-0")

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
