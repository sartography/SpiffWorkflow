# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import sys, unittest, re, os
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.storage import DictionarySerializer
from .SerializerTest import SerializerTest, SerializeEveryPatternTest

class DictionarySerializerTest(SerializerTest):
    CORRELATE = DictionarySerializer

    def setUp(self):
        SerializerTest.setUp(self)
        self.serializer = DictionarySerializer()
        self.serial_type = dict

    def compareSerialization(self, dict1, dict2):
        for key1, value1 in dict1.items():
            if key1 not in dict2:
                raise Exception("Missing Key: " + key1)
            value2 = dict2[key1]
            if isinstance(value1, dict):
                try:
                    self.compareSerialization(value1, value2)
                except Exception as e:
                    raise Exception(key1 + '/' + str(e))
            else:
                if value1 != value2:
                    raise Exception("Unequal: " + key1 + '=' + repr(value1) \
                                    + " vs " + repr(value2))

    def testConstructor(self):
        DictionarySerializer()


class DictionarySerializeEveryPatternTest(SerializeEveryPatternTest):

    def setUp(self):
        super(DictionarySerializeEveryPatternTest, self).setUp()
        self.serializerTestClass = DictionarySerializerTest(methodName='testConstructor')
        self.serializerTestClass.setUp()


def suite():
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(DictionarySerializerTest)
    tests.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(DictionarySerializeEveryPatternTest))
    return tests
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
