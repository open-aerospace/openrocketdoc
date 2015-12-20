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
            document.Nosecone(""),
            document.Bodytube("body"),
        ]
        rocket.stages = [stage0]

    def test_stage_mass_sum(self):
        stage0 = document.Stage("Booster")
        stage0.components = [
            document.Nosecone("", mass=0.7),
            document.Bodytube("body"),
            document.Bodytube("body", mass=24.1),
        ]
        self.assertEqual(24.8, stage0.mass)

    def test_rocket_mass_sum(self):
        stage0 = document.Stage("Booster")
        stage0.components = [
            document.Nosecone("", mass=0.7),
            document.Bodytube("body"),
            document.Bodytube("body", mass=24.1),
        ]
        stage1 = document.Stage("Booster")
        stage1.components = [
            document.Bodytube("body", mass=4.87),
            document.Fin(mass=0.1),
        ]

        rocket = document.Rocket("Rocket")
        rocket.stages = [stage0, stage1]

        self.assertEqual(29.77, rocket.mass)

    def test_fins(self):
        fin = document.Fin()
        self.assertEqual(0, fin.mass)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
