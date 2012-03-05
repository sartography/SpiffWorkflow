import sys, unittest, re, os
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..', '..', '..', 'src'))

from PatternTest import run_workflow
from SpiffWorkflow.storage.Serializer import Serializer
from SpiffWorkflow.specs import WorkflowSpec
from data.spiff.workflow1 import TestWorkflowSpec

def assert_equal(dict1, dict2):
    for key1, value1 in dict1.iteritems():
        if key1 not in dict2:
            raise Exception("Missing Key: " + key1)
        value2 = dict2[key1]
        if isinstance(value1, dict):
            try:
                assert_equal(value1, value2)
            except Exception, e:
                raise Exception(key1 + '/' + str(e))
        else:
            if value1 != value2:
                raise Exception("Unequal: " + key1 + '=' + repr(value1) \
                                + " vs " + repr(value2))

class SerializerTest(unittest.TestCase):
    CORRELATE = Serializer

    def setUp(self):
        self.wf_spec = TestWorkflowSpec()
        self.serializer = None

    def testConstructor(self):
        Serializer()

    def testSerializeWorkflowSpec(self):
        if self.serializer is None:
            return

        # Back to back testing.
        serialized1 = self.wf_spec.serialize(self.serializer)
        wf_spec     = WorkflowSpec.deserialize(self.serializer, serialized1)
        serialized2 = wf_spec.serialize(self.serializer)
        self.assert_(isinstance(serialized1, dict))
        self.assert_(isinstance(serialized2, dict))
        assert_equal(serialized1, serialized2)
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
