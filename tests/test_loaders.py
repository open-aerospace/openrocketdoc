#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_loaders
----------------------------------

Tests for `loaders` module.
"""

from __future__ import print_function
import unittest
# import json
from openrocketdoc import loaders


class TestLoaders(unittest.TestCase):

    def setUp(self):
        pass

    def test_read_openrocket_14_zip(self):
        ork = loaders.Openrocket()
        ork.load('tests/data/example_simple_1.ork')

        # print(json.dumps(ork.rocket, indent=4, separators=(',', ': ')))

        # Expected traits for this file:
        self.assertEqual(ork.or_version, '1.4')
        self.assertEqual(ork.rocket['name'], 'Rocket')
        self.assertEqual(len(ork.rocket['stages']), 1)

    def test_read_RockSimEng(self):
        rse_loader = loaders.RockSimEngine()
        rse = rse_loader.load('tests/data/motor_f10.rse')

        # Some expected traits for this file
        self.assertEqual(rse.name, "F10")
        self.assertEqual(rse.manufacturer, "Apogee")
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
        eng = loaders.RaspEngine()
        eng.load('tests/data/motor_f10.eng')

        # print(json.dumps(eng.engine, indent=4, separators=(',', ': ')))

        # Some expected traits for this file
        self.assertGreater(len(eng.engine['Comments']), 50)
        self.assertEqual(eng.engine['Name'], "F10")
        self.assertAlmostEqual(eng.engine['Diameter'], 0.029)
        self.assertAlmostEqual(eng.engine['Length'], 0.093)
        self.assertAlmostEqual(eng.engine['Propellent weight'], 0.0407)
        self.assertAlmostEqual(eng.engine['Initial weight'], 0.0841)
        self.assertEqual(eng.engine['Manufacturer'], "Apogee")
        self.assertEqual(len(eng.engine['Thrustcurve']), 27)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
