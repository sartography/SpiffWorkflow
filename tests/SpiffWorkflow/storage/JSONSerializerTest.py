# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import sys, unittest, re, os
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.storage import JSONSerializer
from .SerializerTest import SerializerTest, SerializeEveryPatternTest
from .DictionarySerializerTest import DictionarySerializerTest
import json

class JSONSerializerTest(SerializerTest):
    CORRELATE = JSONSerializer

    def setUp(self):
        SerializerTest.setUp(self)
        self.serializer = JSONSerializer()
        self.serial_type = str

    def testConstructor(self):
        JSONSerializer()

    def compareSerialization(self, s1, s2, exclude_dynamic=False):
        obj1 = json.loads(s1)
        obj2 = json.loads(s2)
        #print(s1)
        #print(s2)
        if exclude_dynamic:
            exclude_items = ['__uuid__']
        else:
            exclude_items = []
        DictionarySerializerTest(methodName='testConstructor').compareSerialization(obj1, obj2,
                                                                                    exclude_dynamic=exclude_dynamic,
                                                                                    exclude_items=exclude_items)

class JSONSerializeEveryPatternTest(SerializeEveryPatternTest):

    def setUp(self):
        super(JSONSerializeEveryPatternTest, self).setUp()
        self.serializerTestClass = JSONSerializerTest(methodName='testConstructor')
        self.serializerTestClass.setUp()


def suite():
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(JSONSerializerTest)
    tests.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(JSONSerializeEveryPatternTest))
    return tests
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
