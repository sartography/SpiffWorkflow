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
    maxDiff = None

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
            self.assertIsInstance(item2, dict)
            for key, value in item1.items():
                self.assertIn(key, item2)
                if key in exclude_items:
                    continue
                self.compareSerialization(value, item2[key], exclude_dynamic=exclude_dynamic, exclude_items=exclude_items)

            for key, _ in item2.items():
                self.assertIn(key, item1)
                
        elif isinstance(item1, list):
            if not isinstance(item2, list):
                raise Exception(": companion item is not a list (is a " + str(type(item2)) + ")")
            if not len(item1) == len(item2):
                raise Exception(": companion list is not the same length: " + str(len(item1)) + " v " + str(len(item2)))
            for i, listitem in enumerate(item1):
                self.compareSerialization(listitem, item2[i], exclude_dynamic=exclude_dynamic, exclude_items=exclude_items)

        elif isinstance(item1, Workflow):
            raise Exception("Item is a Workflow")
        
        else:
            if type(item1) != type(item2):
                raise Exception(": companion item is not the same type (is a " + str(type(item2)) + "): " + str(item1) + " v " + str(item2))
            if type(item1) in exclude_items:
                return
            self.assertEqual(item1, item2)
        

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
