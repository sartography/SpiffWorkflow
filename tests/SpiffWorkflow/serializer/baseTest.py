# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
import sys
import unittest
import re
import os
import warnings
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..'))

from uuid import UUID
from PatternTest import run_workflow, PatternTest
from SpiffWorkflow.serializer.base import Serializer
from SpiffWorkflow.specs import WorkflowSpec
from SpiffWorkflow import Workflow
from SpiffWorkflow.serializer.exceptions import TaskSpecNotSupportedError, \
    TaskNotSupportedError
from data.spiff.workflow1 import TestWorkflowSpec


class SerializerTest(PatternTest):

    def setUp(self):
        super(SerializerTest, self).setUp()
        self.serializer = Serializer()
        self.return_type = None

    def _prepare_result(self, item):
        return item

    def _compare_results(self, item1, item2, exclude_dynamic=False,
                         exclude_items=None):
        self.assertEqual(item1, item2)

    def _test_roundtrip_serialization(self, obj):
        # Test round trip serialization.
        try:
            serialized1 = obj.serialize(self.serializer)
            restored = obj.__class__.deserialize(self.serializer, serialized1)
            serialized2 = restored.serialize(self.serializer)
        except TaskNotSupportedError as e:
            warnings.warn('unsupported task spec: ' + str(e))
            return

        self.assertIsInstance(serialized1, self.return_type)
        self.assertIsInstance(serialized2, self.return_type)
        serialized1 = self._prepare_result(serialized1)
        serialized2 = self._prepare_result(serialized2)
        self._compare_results(serialized1, serialized2)
        return serialized1

    def _test_workflow_spec(self, test):
        spec_result1 = self._test_roundtrip_serialization(test.spec)
        spec_result2 = self._test_roundtrip_serialization(test.spec)
        self.assertEqual(spec_result1, spec_result2)
        self._compare_results(spec_result1, spec_result2)

        workflow = run_workflow(self, test.spec, test.path, test.data)
        spec_result3 = self._test_roundtrip_serialization(test.spec)
        wf_result3 = self._test_roundtrip_serialization(workflow)
        # We can't compare spec_result 2 and 3, because starting a workflow
        # implicitely causes a Root node to be added to the workflow spec.
        # (No, that doesn't seem to be a clean solution.)
        # self.assertEqual(spec_result2, spec_result3)
        # self._compare_results(spec_result2, spec_result3)

    def testWorkflowSpec(self):
        if type(self.serializer) is Serializer:
            spec = self.workflows[0].spec
            wf = Workflow(spec)
            self.assertRaises(NotImplementedError, spec.serialize,
                              self.serializer)
            self.assertRaises(NotImplementedError,
                              WorkflowSpec.deserialize, self.serializer, None)
            self.assertRaises(NotImplementedError, wf.serialize,
                              self.serializer)
            self.assertRaises(NotImplementedError,
                              Workflow.deserialize, self.serializer, None)
            return

        for test in self.workflows:
            print(test.filename)
            self._test_workflow_spec(test)


def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(SerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
