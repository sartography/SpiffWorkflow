# -*- coding: utf-8 -*-
from __future__ import division
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'SpiffWorkflow')
from version import __version__
from setuptools import setup, find_packages
from os.path import dirname, join

setup(name             = 'SpiffWorkflow',
      version          = __version__,
      description      = 'A workflow framework based on www.workflowpatterns.com',
      long_description = \
"""
Spiff Workflow is a library implementing workflows in pure Python.
It was designed to provide a clean API, and tries to be very easy to use.

You can find a list of supported workflow patterns in the `README file`_
included with the package.
.. _README file: https://github.com/knipknap/SpiffWorkflow/blob/master/README.md
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'lGPLv2',
      packages         = find_packages(exclude=['tests', 'tests.*']),
      install_requires = ['future', 'configparser', 'lxml', 'celery', 'python-Levenshtein'],
      keywords         = 'spiff workflow bpmn engine',
      url              = 'https://github.com/knipknap/SpiffWorkflow',
      classifiers      = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
