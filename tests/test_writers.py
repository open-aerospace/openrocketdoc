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

    def test_write_raspengine(self):
        engine = rdoc.Engine("test engine")

        self.assertEqual(engine.name, "test engine")

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
