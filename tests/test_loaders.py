#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_loaders
----------------------------------

Tests for `loaders` module.
"""

from __future__ import print_function
import unittest
import json
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
        rse = loaders.RockSimEngine()
        rse.load('tests/data/motor_f10.rse')

        # Some expected traits for this file
        self.assertEqual(rse.engine['Name'], "F10")
        self.assertEqual(rse.engine['Manafacturer'], "Apogee")
        self.assertEqual(len(rse.engine['Thrustcurve']), 28)
        self.assertAlmostEqual(rse.engine['Average thrust'], 10.706)
        self.assertAlmostEqual(rse.engine['Burn time'], 7.13)
        self.assertAlmostEqual(rse.engine['Propellent weight'], 0.0407)
        self.assertAlmostEqual(rse.engine['Inital Weight'], 0.0841)
        self.assertAlmostEqual(rse.engine['Diameter'], 0.029)
        self.assertAlmostEqual(rse.engine['Total impulse'], 76.335)
        self.assertAlmostEqual(rse.engine['Isp'], 191.25)
        self.assertAlmostEqual(rse.engine['Length'], 0.093)
        self.assertAlmostEqual(rse.engine['Peak thrust'], 28.22)
        self.assertAlmostEqual(rse.engine['Mass fraction'], 48.39)

        #print(json.dumps(rse.engine, indent=4, separators=(',', ': ')))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
