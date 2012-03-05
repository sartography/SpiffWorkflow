import sys, unittest, re, os
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..', '..', '..', 'src'))

from SpiffWorkflow.storage import XmlSerializer
from xml.parsers.expat import ExpatError
from SerializerTest import SerializerTest

class XmlSerializerTest(SerializerTest):
    CORRELATE = XmlSerializer

    def setUp(self):
        self.serializer = XmlSerializer()

    def get_state(self):
        return open(os.path.join(data_dir, 'spiff', 'workflow1.xml')).read()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(XmlSerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
