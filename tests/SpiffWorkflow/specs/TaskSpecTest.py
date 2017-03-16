# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
import sys
import unittest
import re
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from SpiffWorkflow.specs import WorkflowSpec, Simple, Join
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.specs import TaskSpec
from SpiffWorkflow.serializer.dict import DictionarySerializer

class TaskSpecTest(unittest.TestCase):
    CORRELATE = TaskSpec

    def create_instance(self):
        if 'testtask' in self.wf_spec.task_specs:
            del self.wf_spec.task_specs['testtask']
        return TaskSpec(self.wf_spec, 'testtask', description='foo')

    def setUp(self):
        self.wf_spec = WorkflowSpec()
        self.spec = self.create_instance()

    def testConstructor(self):
        self.assertEqual(self.spec.name, 'testtask')
        self.assertEqual(self.spec.description, 'foo')
        self.assertEqual(self.spec.data, {})
        self.assertEqual(self.spec.defines, {})
        self.assertEqual(self.spec.pre_assign, [])
        self.assertEqual(self.spec.post_assign, [])
        self.assertEqual(self.spec.locks, [])

    def testSetData(self):
        self.assertEqual(self.spec.get_data('foo'), None)
        self.assertEqual(self.spec.get_data('foo', 'bar'), 'bar')
        self.spec.set_data(foo='foobar')
        self.assertEqual(self.spec.get_data('foo'), 'foobar')
        self.assertEqual(self.spec.get_data('foo', 'bar'), 'foobar')

    def testGetData(self):
        return self.testSetData()

    def testConnect(self):
        self.assertEqual(self.spec.outputs, [])
        self.assertEqual(self.spec.inputs, [])
        spec = self.create_instance()
        self.spec.connect(spec)
        self.assertEqual(self.spec.outputs, [spec])
        self.assertEqual(spec.inputs, [self.spec])

    def testFollow(self):
        self.assertEqual(self.spec.outputs, [])
        self.assertEqual(self.spec.inputs, [])
        spec = self.create_instance()
        self.spec.follow(spec)
        self.assertEqual(spec.outputs, [self.spec])
        self.assertEqual(self.spec.inputs, [spec])

    def testTest(self):
        # Should fail because the TaskSpec has no id yet.
        spec = self.create_instance()
        self.assertRaises(WorkflowException, spec.test)

        # Should fail because the task has no inputs.
        self.spec.id = 1
        self.assertRaises(WorkflowException, spec.test)

        # Connect another task to make sure that it has an input.
        self.spec.connect(spec)
        self.assertEqual(spec.test(), None)

    def testSerialize(self):
        serializer = DictionarySerializer()
        spec = self.create_instance()

        try:
            serialized = spec.serialize(serializer)
            self.assertIsInstance(serialized, dict)
        except NotImplementedError:
            self.assertIsInstance(spec, TaskSpec)
            self.assertRaises(NotImplementedError,
                              spec.__class__.deserialize, None, None, None)
            return

        new_wf_spec = WorkflowSpec()
        new_spec = spec.__class__.deserialize(serializer, new_wf_spec,
                serialized)
        before = spec.serialize(serializer)
        after = new_spec.serialize(serializer)
        self.assertEqual(before, after, 'Before:\n%s\nAfter:\n%s\n' % (before,
                after))

    def testAncestors(self):
        T1 = Simple(self.wf_spec, 'T1')
        T2A = Simple(self.wf_spec, 'T2A')
        T2B = Simple(self.wf_spec, 'T2B')
        M = Join(self.wf_spec, 'M')
        T3 = Simple(self.wf_spec, 'T3')

        T1.follow(self.wf_spec.start)
        T2A.follow(T1)
        T2B.follow(T1)
        T2A.connect(M)
        T2B.connect(M)
        T3.follow(M)

        self.assertEquals(T1.ancestors(), [self.wf_spec.start])
        self.assertEquals(T2A.ancestors(), [T1, self.wf_spec.start])
        self.assertEquals(T2B.ancestors(), [T1, self.wf_spec.start])
        self.assertEquals(M.ancestors(), [T2A, T1, self.wf_spec.start, T2B])
        self.assertEqual(len(T3.ancestors()), 5)

    def test_ancestors_cyclic(self):
        T1 = Join(self.wf_spec, 'T1')
        T2 = Simple(self.wf_spec, 'T2')

        T1.follow(self.wf_spec.start)
        T2.follow(T1)
        T1.connect(T2)

        self.assertEquals(T1.ancestors(), [self.wf_spec.start])
        self.assertEquals(T2.ancestors(), [T1, self.wf_spec.start])


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TaskSpecTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
