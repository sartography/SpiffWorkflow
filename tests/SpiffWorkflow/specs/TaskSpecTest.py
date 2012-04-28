import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from SpiffWorkflow.specs import WorkflowSpec
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.specs.TaskSpec import TaskSpec
from SpiffWorkflow.storage import DictionarySerializer, JSONSerializer


class TaskSpecTest(unittest.TestCase):
    CORRELATE = TaskSpec

    def create_instance(self):
        return TaskSpec(self.wf_spec, 'testtask', description='foo')

    def setUp(self):
        self.wf_spec = WorkflowSpec()
        self.spec = self.create_instance()

    def testConstructor(self):
        self.assertEqual(self.spec.name, 'testtask')
        self.assertEqual(self.spec.description, 'foo')
        self.assertEqual(self.spec.properties, {})
        self.assertEqual(self.spec.defines, {})
        self.assertEqual(self.spec.pre_assign, [])
        self.assertEqual(self.spec.post_assign, [])
        self.assertEqual(self.spec.locks, [])

    def testSetProperty(self):
        self.assertEqual(self.spec.get_property('foo'), None)
        self.assertEqual(self.spec.get_property('foo', 'bar'), 'bar')
        self.spec.set_property(foo='foobar')
        self.assertEqual(self.spec.get_property('foo'), 'foobar')
        self.assertEqual(self.spec.get_property('foo', 'bar'), 'foobar')

    def testGetProperty(self):
        return self.testSetProperty()

    def testConnect(self):
        self.assertEqual(self.spec.outputs, [])
        spec = self.create_instance()
        self.spec.connect(spec)
        self.assertEqual(self.spec.outputs, [spec])
        self.assertEqual(spec.inputs, [self.spec])

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
        serialized = spec.serialize(serializer)
        self.assert_(isinstance(serialized, dict))
        new_spec = spec.__class__.deserialize(serializer, self.wf_spec,
                serialized)
        before = spec.serialize(serializer)
        after = new_spec.serialize(serializer)
        self.assertEqual(before, after, 'Before:\n%s\nAfter:\n%s\n' % (before,
                after))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TaskSpecTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
