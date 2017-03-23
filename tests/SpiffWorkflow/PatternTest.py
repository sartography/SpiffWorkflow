# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
from builtins import object
import sys
import unittest
import re
import os
import glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from SpiffWorkflow.specs import *
from SpiffWorkflow import Task
from SpiffWorkflow.serializer.prettyxml import XmlSerializer
from util import run_workflow


class WorkflowTestData(object):

    def __init__(self, filename, spec, path, data):
        self.filename = filename
        self.spec = spec
        self.path = path
        self.data = data


class PatternTest(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        Task.id_pool = 0
        Task.thread_id_pool = 0
        self.xml_path = ['data/spiff/control-flow',
                         'data/spiff/data',
                         'data/spiff/resource',
                         'data/spiff']
        self.workflows = []

        for basedir in self.xml_path:
            dirname = os.path.join(os.path.dirname(__file__), basedir)

            for filename in os.listdir(dirname):
                if not filename.endswith(('.xml', '.py')):
                    continue
                if filename.endswith('__.py'):
                    continue
                filename = os.path.join(dirname, filename)
                self.load_workflow_spec(filename)

    def load_workflow_spec(self, filename):
        # Load the .path file.
        path_file = os.path.splitext(filename)[0] + '.path'
        if os.path.exists(path_file):
            expected_path = open(path_file).read()
        else:
            expected_path = None

        # Load the .data file.
        data_file = os.path.splitext(filename)[0] + '.data'
        if os.path.exists(data_file):
            expected_data = open(data_file, 'r').read()
        else:
            expected_data = None

        # Test patterns that are defined in XML format.
        if filename.endswith('.xml'):
            xml = open(filename).read()
            serializer = XmlSerializer()
            wf_spec = WorkflowSpec.deserialize(
                serializer, xml, filename=filename)

        # Test patterns that are defined in Python.
        elif filename.endswith('.py'):
            code = compile(open(filename).read(), filename, 'exec')
            thedict = {}
            result = eval(code, thedict)
            wf_spec = thedict['TestWorkflowSpec']()

        else:
            raise Exception('unsuported specification format', filename)

        test_data = WorkflowTestData(
            filename, wf_spec, expected_path, expected_data)
        self.workflows.append(test_data)

    def testWorkflowSpec(self):
        for test in self.workflows:
            print(test.filename)
            run_workflow(self, test.spec, test.path, test.data)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PatternTest)
if __name__ == '__main__':
    if len(sys.argv) == 2:
        test = PatternTest('run_pattern')
        test.setUp()
        test.run_pattern(sys.argv[1])
        sys.exit(0)
    unittest.TextTestRunner(verbosity=2).run(suite())
