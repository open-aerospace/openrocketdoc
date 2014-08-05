#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Component(object):

    def __init__(self):
        self.name = ''
        self.mass = 0.0
        self.length = 0.0


class Nosecone(Component):

    def __init__(self):
        self.shape = ''
        self.thickness = 0

