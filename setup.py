# -*- coding: utf-8 -*-
import pathlib
import sys

sys.path.insert(0, '.')
sys.path.insert(0, 'SpiffWorkflow')
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='SpiffWorkflow',
      version='1.2.0',
      description='A workflow framework and BPMN/DMN Processor',
      long_description=README,
      long_description_content_type="text/markdown",
      author='Sartography',
      author_email='dan@sartography.com',
      license='lGPLv2',
      packages=find_packages(exclude=['tests', 'tests.*']),
      install_requires=['configparser', 'lxml', 'celery', 'dateparser', 'pytz',
          # required for python 3.7 - https://stackoverflow.com/a/73932581
          'importlib-metadata<5.0'],
      keywords='spiff workflow bpmn engine',
      url='https://github.com/sartography/SpiffWorkflow',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Programming Language :: Python',
          'Topic :: Other/Nonlisted Topic',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ])
