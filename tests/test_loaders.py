#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_loaders
----------------------------------

Tests for `loaders` module.
"""

from __future__ import print_function
import unittest
from openrocketdoc import loaders
# from openrocketdoc import writers


class TestLoaders(unittest.TestCase):

    def setUp(self):
        pass

    def test_read_openrocket_14_zip(self):
        ork = loaders.Openrocket().load('tests/data/example_simple_1.ork')

        # print(writers.Document().dump(ork))

        # Expected traits for this file:
        self.assertEqual(ork.name, 'Rocket')
        self.assertEqual(len(ork.stages), 1)
        self.assertEqual(ork.stages[0].name, "Sustainer")
        self.assertEqual(ork.stages[0].components[0].name, "Nosecone")
        self.assertAlmostEqual(ork.stages[0].components[0].length, 0.15)
        self.assertEqual(ork.stages[0].components[0].color, (165, 165, 165))
        self.assertAlmostEqual(ork.stages[0].components[1].length, 0.3)

    def test_read_RockSimEng(self):
        rse_loader = loaders.RockSimEngine()
        rse = rse_loader.load('tests/data/motor_f10.rse')

        # Some expected traits for this file
        self.assertEqual(rse.name, "F10")
        self.assertEqual(rse.manufacturer, "Apogee")
        self.assertGreater(len(rse.comments), 50)
        self.assertEqual(len(rse.thrustcurve), 28)
        self.assertAlmostEqual(rse.thrust_avg, 10.706, places=3)
        self.assertAlmostEqual(rse.I_total, 76.335, places=3)
        self.assertAlmostEqual(rse.t_burn, 7.13)
        self.assertAlmostEqual(rse.m_prop, 0.0407)
        self.assertAlmostEqual(rse.m_init, 0.0841)
        self.assertAlmostEqual(rse.diameter, 0.029)
        self.assertAlmostEqual(rse.I_total, 76.335, places=3)
        self.assertAlmostEqual(rse.Isp, 191.25, places=2)
        self.assertAlmostEqual(rse.length, 0.093)
        self.assertAlmostEqual(rse.thrust_peak, 28.22)
        self.assertAlmostEqual(rse.m_frac, 48.39, places=2)

    def test_read_RaspEng(self):
        eng_loader = loaders.RaspEngine()
        eng = eng_loader.load('tests/data/motor_f10.eng')

        # Some expected traits for this file
        self.assertGreater(len(eng.comments), 50)
        self.assertEqual(eng.name, "F10")
        self.assertEqual(eng.manufacturer, "Apogee")
        self.assertAlmostEqual(eng.diameter, 0.029)
        self.assertAlmostEqual(eng.length, 0.093)
        self.assertAlmostEqual(eng.m_prop, 0.0407)
        self.assertAlmostEqual(eng.m_init, 0.0841)
        self.assertAlmostEqual(eng.thrust_avg, 10.706, places=1)
        self.assertAlmostEqual(eng.I_total, 76.335, places=0)
        self.assertAlmostEqual(eng.t_burn, 7.13)
        self.assertAlmostEqual(eng.Isp, 191, places=0)
        self.assertAlmostEqual(eng.thrust_peak, 28.22)
        self.assertAlmostEqual(eng.m_frac, 48.39, places=2)
        self.assertEqual(len(eng.thrustcurve), 27)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
