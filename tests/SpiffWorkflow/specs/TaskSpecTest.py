import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from SpiffWorkflow.specs import WorkflowSpec
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.specs.TaskSpec import TaskSpec

class TaskSpecTest(unittest.TestCase):
    def setUp(self):
        self.wf_spec = WorkflowSpec()
        self.spec = TaskSpec(self.wf_spec, 'testtask', description = 'foo')

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
        self.spec.set_property(foo = 'foobar')
        self.assertEqual(self.spec.get_property('foo'), 'foobar')
        self.assertEqual(self.spec.get_property('foo', 'bar'), 'foobar')

    def testGetProperty(self):
        return self.testSetProperty()

    def testConnect(self):
        self.assertEqual(self.spec.outputs, [])
        spec = TaskSpec(self.wf_spec, 'another')
        self.spec.connect(spec)
        self.assertEqual(self.spec.outputs, [spec])
        self.assertEqual(spec.inputs, [self.spec])

    def testTest(self):
        # Should fail because the TaskSpec has no if yet.
        spec = TaskSpec(self.wf_spec, 'myspec')
        self.assertRaises(WorkflowException, spec.test)

        # Should fail because the task has no inputs.
        self.spec.id = 1
        self.assertRaises(WorkflowException, spec.test)

        # Connect another task to make sure that it has an input.
        self.spec.connect(spec)
        self.assertEqual(spec.test(), None)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TaskSpecTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
