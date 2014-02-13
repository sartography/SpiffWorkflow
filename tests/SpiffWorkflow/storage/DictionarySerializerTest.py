# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import sys, unittest, re, os
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.storage import DictionarySerializer
from .SerializerTest import SerializerTest, SerializeEveryPatternTest
from SpiffWorkflow import Workflow
import uuid

class DictionarySerializerTest(SerializerTest):
    CORRELATE = DictionarySerializer

    def setUp(self):
        SerializerTest.setUp(self)
        self.serializer = DictionarySerializer()
        self.serial_type = dict

    def compareSerialization(self, item1, item2, exclude_dynamic=False, exclude_items=[]):
        if exclude_dynamic:
            if 'last_state_change' not in exclude_items:
                exclude_items.append('last_state_change')
            if 'last_task' not in exclude_items:
                exclude_items.append('last_task')
            if uuid.UUID not in exclude_items:
                exclude_items.append(uuid.UUID)

        if isinstance(item1, dict):
            if not isinstance(item2, dict):
                raise Exception(": companion item is not a dict (is a " + str(type(item2)) + "): " + str(item1) + " v " + str(item2))
            for key, value in item1.items():
                if key not in item2:
                    raise Exception("Missing Key: " + key + " (in 1, not 2)")

                if key in exclude_items:
                    continue
                try:
                    self.compareSerialization(value, item2[key], exclude_dynamic=exclude_dynamic, exclude_items=exclude_items)
                except Exception as e:
                    raise Exception(key + '/' + str(e))

            for key, _ in item2.items():
                if key not in item1:
                    raise Exception("Missing Key: " + key + " (in 2, not 1)")
                
        elif isinstance(item1, list):
            if not isinstance(item2, list):
                raise Exception(": companion item is not a list (is a " + str(type(item2)) + ")")
            if not len(item1) == len(item2):
                raise Exception(": companion list is not the same length: " + str(len(item1)) + " v " + str(len(item2)))
            for i, listitem in enumerate(item1):
                try:
                    self.compareSerialization(listitem, item2[i], exclude_dynamic=exclude_dynamic, exclude_items=exclude_items)
                except Exception as e:
                    raise Exception('[' + str(i) + ']/' + str(e))

        elif isinstance(item1, Workflow):
            raise Exception("Item is a Workflow")
        
        else:
            if type(item1) != type(item2):
                raise Exception(": companion item is not the same type (is a " + str(type(item2)) + "): " + str(item1) + " v " + str(item2))
            if type(item1) in exclude_items:
                return
            if item1 != item2:
                raise Exception("Unequal: " + repr(item1) \
                                + " vs " + repr(item2)) 
        

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
