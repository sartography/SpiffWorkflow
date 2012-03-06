import sys, unittest, re, os
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..', 'src'))

from SpiffWorkflow.storage import DictionarySerializer
from SerializerTest import SerializerTest

class DictionarySerializerTest(SerializerTest):
    CORRELATE = DictionarySerializer

    def setUp(self):
        SerializerTest.setUp(self)
        self.serializer = DictionarySerializer()
        self.serial_type = dict

    def compare_serialized(self, dict1, dict2):
        for key1, value1 in dict1.iteritems():
            if key1 not in dict2:
                raise Exception("Missing Key: " + key1)
            value2 = dict2[key1]
            if isinstance(value1, dict):
                try:
                    self.compare_serialized(value1, value2)
                except Exception, e:
                    raise Exception(key1 + '/' + str(e))
            else:
                if value1 != value2:
                    raise Exception("Unequal: " + key1 + '=' + repr(value1) \
                                    + " vs " + repr(value2))

    def testConstructor(self):
        DictionarySerializer()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DictionarySerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
