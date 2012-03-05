import sys, unittest, re, os
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..', '..', '..', 'src'))

from PatternTest import run_workflow
from SpiffWorkflow.storage.Serializer import Serializer
from SpiffWorkflow.specs import WorkflowSpec
from xml.parsers.expat import ExpatError

class SerializerTest(unittest.TestCase):
    def setUp(self):
        self.serializer = None

    def get_state(self):
        return None

    def testConstructor(self):
        if self.serializer is None:
            return
        Serializer()

    def testDeserializeWorkflowSpec(self):
        if self.serializer is None:
            return
        state         = self.get_state()
        wf_spec       = WorkflowSpec.deserialize(self.serializer, state)
        path_file     = os.path.join(data_dir, 'spiff', 'workflow1.path')
        expected_path = open(path_file).read()
        run_workflow(self, wf_spec, expected_path, None)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
