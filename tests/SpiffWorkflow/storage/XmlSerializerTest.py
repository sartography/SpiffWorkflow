# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division
import sys, unittest, re, os
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.storage import XmlSerializer
from .SerializerTest import SerializerTest
from PatternTest import run_workflow
from SpiffWorkflow.specs import WorkflowSpec

class XmlSerializerTest(SerializerTest):
    def setUp(self):
        super(XmlSerializerTest, self).setUp()
        self.serializer = XmlSerializer()
        self.return_type = str

    def testWorkflowSpec(self):
        # Nothing to test here: The deserialization is already used in setUp()
        # to load all specs, and serialization is not supported.
        pass
        
def suite():
    return unittest.TestLoader().loadTestsFromTestCase(XmlSerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
