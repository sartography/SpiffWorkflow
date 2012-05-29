from setuptools import setup, find_packages
from os.path import dirname, join

setup(name             = 'SpiffWorkflow',
      version          = '0.3.2-rackspace',
      description      = 'A workflow framework based on www.workflowpatterns.com',
      long_description = \
"""
Spiff Workflow is a library implementing workflows in pure Python.
It was designed to provide a clean API, and tries to be very easy to use.

You can find a list of supported workflow patterns in the `README file`_
included with the package.

WARNING! This software is still under development - there are no guarantees
to API stability at this time.

.. _README file: https://github.com/knipknap/SpiffWorkflow/blob/master/README.md
""",
      author           = 'Samuel Abels',
      author_email     = 'cheeseshop.python.org@debain.org',
      license          = 'lGPLv2',
      packages         = find_packages(exclude=['tests', 'tests.*']),
      requires         = [],
      keywords         = 'spiff guard acl acls security authentication object storage',
      url              = 'https://github.com/knipknap/SpiffWorkflow',
      classifiers      = [
        'Development Status :: 3 - Alpha - Rackspace Fork',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
