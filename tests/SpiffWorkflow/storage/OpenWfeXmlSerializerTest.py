import sys, unittest, re, os
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..'))
sys.path.insert(0, os.path.join(dirname, '..', '..', '..', 'src'))

from SpiffWorkflow.storage import OpenWfeXmlSerializer
from xml.parsers.expat import ExpatError
from SerializerTest import SerializerTest

class OpenWfeXmlSerializerTest(SerializerTest):
    CORRELATE = OpenWfeXmlSerializer

    def setUp(self):
        self.serializer = OpenWfeXmlSerializer()

    def get_state(self):
        xml_file  = os.path.join(data_dir, 'openwfe', 'workflow1.xml')
        xml       = open(xml_file).read()
        path_file = os.path.splitext(xml_file)[0] + '.path'
        path      = open(path_file).read()
        return xml, path

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(OpenWfeXmlSerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
