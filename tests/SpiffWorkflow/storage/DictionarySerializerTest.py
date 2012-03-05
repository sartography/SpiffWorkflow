import sys, unittest, re, os
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..', '..', '..', 'src'))

from SpiffWorkflow.specs import WorkflowSpec
from SpiffWorkflow.storage import DictionarySerializer, XmlSerializer
from xml.parsers.expat import ExpatError
from SerializerTest import SerializerTest

class DictionarySerializerTest(SerializerTest):
    CORRELATE = DictionarySerializer

    def setUp(self):
        SerializerTest.setUp(self)
        self.serializer = DictionarySerializer()

    def testConstructor(self):
        DictionarySerializer()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DictionarySerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
