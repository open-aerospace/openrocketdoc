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

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
