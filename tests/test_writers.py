#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_writers
----------------------------------

Tests for `writers` module.
"""

from __future__ import print_function
import unittest
import json
from openrocketdoc import loaders
from openrocketdoc import writers


class TestWriters(unittest.TestCase):

    def setUp(self):
        pass

    def test_write_engine(self):
        eng = loaders.RaspEngine()
        eng.load('tests/data/motor_f10.eng')

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
