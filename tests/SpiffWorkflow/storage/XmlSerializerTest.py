import sys, unittest, re, os
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.storage import XmlSerializer
from xml.parsers.expat import ExpatError
from SerializerTest import SerializerTest
from PatternTest import run_workflow
from SpiffWorkflow.specs import WorkflowSpec

class XmlSerializerTest(SerializerTest):
    CORRELATE = XmlSerializer

    def setUp(self):
        SerializerTest.setUp(self)
        self.serializer = XmlSerializer()
        self.serial_type = str

    def testConstructor(self):
        XmlSerializer()

    def testSerializeWorkflowSpec(self):
        pass # Serialization not yet supported.

    def testDeserializeWorkflowSpec(self):
        xml_file  = os.path.join(data_dir, 'spiff', 'workflow1.xml')
        xml       = open(xml_file).read()
        path_file = os.path.splitext(xml_file)[0] + '.path'
        path      = open(path_file).read()
        wf_spec   = WorkflowSpec.deserialize(self.serializer, xml)

        run_workflow(self, wf_spec, path, None)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(XmlSerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
