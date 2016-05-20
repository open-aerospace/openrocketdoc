#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_writers
----------------------------------

Tests for `writers` module.
"""

from __future__ import print_function
import unittest
from openrocketdoc import document as rdoc
from openrocketdoc import loaders
from openrocketdoc import writers


class TestWriters(unittest.TestCase):

    def setUp(self):
        pass

    def test_write_document_smoke(self):
        rocket = rdoc.Rocket("Rocket")
        stage0 = rdoc.Stage("Sustainer")
        stage0.components = [
            rdoc.Nosecone(rdoc.Noseshape.VONKARMAN, 1, 0.2, 1.0),
            rdoc.Bodytube("body", 1, 0.2),
        ]
        rocket.stages = [stage0]
        str_file = writers.Document().dump(rocket)

        # print("Output:")
        # print(str_file)

        self.assertGreater(len(str_file), 10)

    def test_convert_ork(self):
        ork = loaders.Openrocket()
        rocket = ork.load('tests/data/example_simple_1.ork')
        str_file = writers.Document().dump(rocket)

        # print("Output:")
        # print(str_file)

        self.assertGreater(len(str_file), 10)

    def test_write_blank_raspEngine(self):
        engine = rdoc.Engine("test engine")
        str_file = writers.RaspEngine().dump(engine)

        # smoketest
        self.assertGreater(len(str_file), 10)

    def test_write_blank_rocksimEngine(self):
        engine = rdoc.Engine("test engine")
        str_file = writers.RockSimEngine().dump(engine)

        # smoketest
        self.assertGreater(len(str_file), 50)

    def test_write_simple_JSBSimEngine(self):
        engine = rdoc.Engine("test engine")
        engine.manufacturer = "Open Aerospace"
        engine.length = 0.1
        engine.diameter = 0.2
        engine.Isp = 169
        engine.m_prop = 1.0
        engine.thrust_avg = 1000
        str_file = writers.JSBSimEngine.dump(engine)

        # smoke test
        self.assertGreater(len(str_file), 50)

    def test_RockSim_to_JSBSimEngine(self):
        engine = loaders.RockSimEngine().load('tests/data/motor_N2501.rse')
        str_file = writers.JSBSimEngine.dump(engine)

        # smoke test
        self.assertGreater(len(str_file), 50)

    def test_write_simple_rocksimEngine(self):
        engine = rdoc.Engine("test engine")
        engine.manufacturer = "Open Aerospace"
        engine.length = 0.1
        engine.diameter = 0.2
        engine.Isp = 169
        engine.m_prop = 1.0
        engine.thrust_avg = 1000
        str_file = writers.RockSimEngine().dump(engine)

        # smoke test
        self.assertGreater(len(str_file), 50)

        # re-read into loader, it should still parse
        reloaded_motor = loaders.RockSimEngine().load(str_file)
        self.assertEqual(reloaded_motor.comments, None)
        self.assertEqual(reloaded_motor.name, "test engine")
        self.assertEqual(reloaded_motor.manufacturer, "Open Aerospace")
        self.assertAlmostEqual(reloaded_motor.diameter, 0.2)
        self.assertAlmostEqual(reloaded_motor.length, 0.1)
        self.assertAlmostEqual(reloaded_motor.m_prop, 1.0)
        self.assertAlmostEqual(reloaded_motor.m_init, 1.0)
        self.assertAlmostEqual(reloaded_motor.thrust_avg, 1000.0, places=1)
        self.assertAlmostEqual(reloaded_motor.I_total, 1105.0, places=0)
        self.assertAlmostEqual(reloaded_motor.t_burn, 1.105, places=3)
        self.assertAlmostEqual(reloaded_motor.thrust_peak, 1000.0)
        self.assertAlmostEqual(reloaded_motor.m_frac, 100.00, places=2)

    def test_write_simple_raspengine(self):
        engine = rdoc.Engine("test engine")
        engine.manufacturer = "Open Aerospace"
        engine.length = 0.1
        engine.diameter = 0.2
        engine.Isp = 169
        engine.m_prop = 1.0
        engine.thrust_avg = 1000
        str_file = writers.RaspEngine().dump(engine)

        # smoke test
        self.assertGreater(len(str_file), 10)

        # re-read into loader, it should still parse
        eng_loader = loaders.RaspEngine()
        reloaded_motor = eng_loader.load(str_file)
        self.assertGreater(len(reloaded_motor.comments), 0)
        self.assertEqual(reloaded_motor.name, "test-engine")
        self.assertEqual(reloaded_motor.manufacturer, "Open-Aerospace")
        self.assertAlmostEqual(reloaded_motor.diameter, 0.2)
        self.assertAlmostEqual(reloaded_motor.length, 0.1)
        self.assertAlmostEqual(reloaded_motor.m_prop, 1.0)
        self.assertAlmostEqual(reloaded_motor.m_init, 1.0)
        self.assertAlmostEqual(reloaded_motor.thrust_avg, 1000.0, places=1)
        self.assertAlmostEqual(reloaded_motor.I_total, 1105.0, places=0)
        self.assertAlmostEqual(reloaded_motor.t_burn, 1.105)
        self.assertAlmostEqual(reloaded_motor.thrust_peak, 1000.0)
        self.assertAlmostEqual(reloaded_motor.m_frac, 100.00, places=2)

    def test_rewrite_raspengine(self):
        eng_loader = loaders.RaspEngine()
        motor_f10 = eng_loader.load('tests/data/motor_f10.eng')

        rasp_writer = writers.RaspEngine()
        str_file = rasp_writer.dump(motor_f10)
        # smoke test, something happend?
        self.assertGreater(len(str_file), 100)

        # re-read into loader, it should still parse
        eng_loader = loaders.RaspEngine()
        reloaded_motor_f10 = eng_loader.load(str_file)
        self.assertGreater(len(reloaded_motor_f10.comments), 50)
        self.assertEqual(reloaded_motor_f10.name, "F10")
        self.assertEqual(reloaded_motor_f10.manufacturer, "Apogee")
        self.assertAlmostEqual(reloaded_motor_f10.diameter, 0.029)
        self.assertAlmostEqual(reloaded_motor_f10.length, 0.093)
        self.assertAlmostEqual(reloaded_motor_f10.m_prop, 0.0407)
        self.assertAlmostEqual(reloaded_motor_f10.m_init, 0.0841)
        self.assertAlmostEqual(reloaded_motor_f10.thrust_avg, 10.706, places=1)
        self.assertAlmostEqual(reloaded_motor_f10.I_total, 76.335, places=0)
        self.assertAlmostEqual(reloaded_motor_f10.t_burn, 7.13)
        self.assertAlmostEqual(reloaded_motor_f10.Isp, 191, places=0)
        self.assertAlmostEqual(reloaded_motor_f10.thrust_peak, 28.22)
        self.assertAlmostEqual(reloaded_motor_f10.m_frac, 48.39, places=2)
        self.assertEqual(len(reloaded_motor_f10.thrustcurve), 27)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
