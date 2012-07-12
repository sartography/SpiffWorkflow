import sys, unittest, re, os
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..'))

from PatternTest import run_workflow
from SpiffWorkflow.storage.Serializer import Serializer
from SpiffWorkflow.specs import WorkflowSpec
from data.spiff.workflow1 import TestWorkflowSpec

class SerializerTest(unittest.TestCase):
    CORRELATE = Serializer

    def setUp(self):
        self.wf_spec = TestWorkflowSpec()
        self.serializer = None
        self.serial_type = None

    def compare_serialized(self, state1, state2):
        return state1 == state2

    def testConstructor(self):
        Serializer()

    def testSerializeWorkflowSpec(self):
        if self.serializer is None:
            return

        # Back to back testing.
        serialized1 = self.wf_spec.serialize(self.serializer)
        wf_spec     = WorkflowSpec.deserialize(self.serializer, serialized1)
        serialized2 = wf_spec.serialize(self.serializer)
        self.assert_(isinstance(serialized1, self.serial_type))
        self.assert_(isinstance(serialized2, self.serial_type))
        self.compare_serialized(serialized1, serialized2)
        self.assertEqual(serialized1, serialized2)

        # Test whether the restored workflow still works.
        path_file = os.path.join(data_dir, 'spiff', 'workflow1.path')
        path      = open(path_file).read()
        run_workflow(self, wf_spec, path, None)

    def testDeserializeWorkflowSpec(self):
        pass # Already covered in testSerializeWorkflowSpec()

    def testSerializeWorkflow(self):
        pass #TODO

    def testDeserializeWorkflow(self):
        pass #TODO

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
