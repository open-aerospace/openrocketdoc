#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from zipfile import ZipFile


class Openrocket(object):

    def __init__(self):
        pass

    def load(self, filename):
        zf = ZipFile(filename)
        print(zf.read(zf.namelist()[0]))
