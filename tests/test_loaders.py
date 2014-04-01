#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_loaders
----------------------------------

Tests for `loaders` module.
"""

import unittest
from openrocketdoc import loaders


class TestLoaders(unittest.TestCase):

    def setUp(self):
        pass

    def test_read_openrocket(self):
        OR = loaders.Openrocket()
        OR.load('tests/data/example_simple_1.ork')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
