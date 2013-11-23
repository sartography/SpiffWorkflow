# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import sys, unittest, re, os
dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.storage import JSONSerializer
from .SerializerTest import SerializerTest
import json

class JSONSerializerTest(SerializerTest):
    CORRELATE = JSONSerializer

    def setUp(self):
        SerializerTest.setUp(self)
        self.serializer = JSONSerializer()
        self.serial_type = str

    def testConstructor(self):
        JSONSerializer()

    def compareSerialization(self, s1, s2):
        self.assertEqual(json.loads(s1), json.loads(s2))

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(JSONSerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
