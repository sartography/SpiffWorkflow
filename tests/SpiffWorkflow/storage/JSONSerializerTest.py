import sys, unittest, re, os
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.storage import JSONSerializer
from SerializerTest import SerializerTest

class JSONSerializerTest(SerializerTest):
    CORRELATE = JSONSerializer

    def setUp(self):
        SerializerTest.setUp(self)
        self.serializer = JSONSerializer()
        self.serial_type = str

    def testConstructor(self):
        JSONSerializer()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(JSONSerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
