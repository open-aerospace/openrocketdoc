#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='openrocketdoc',
    version='0.1.0',
    description='Open document format for describing sounding rockets. Includes many useful format transformations for use with scientific computing packages.',
    long_description=readme + '\n\n' + history,
    author='Nathan Bergey',
    author_email='nathan.bergey@gmail.com',
    url='https://github.com/natronics/openrocketdoc',
    packages=[
        'openrocketdoc',
    ],
    package_dir={'openrocketdoc': 'openrocketdoc'},
    include_package_data=True,
    install_requires=[
    ],
    license="GPLv3",
    zip_safe=False,
    keywords='openrocketdoc openrocket ord aerospace simulation',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Scientists',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)
