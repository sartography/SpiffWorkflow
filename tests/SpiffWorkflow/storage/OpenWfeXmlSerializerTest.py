# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import sys, unittest, re, os
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..'))
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.storage import OpenWfeXmlSerializer
from xml.parsers.expat import ExpatError
from .SerializerTest import SerializerTest
from PatternTest import run_workflow
from SpiffWorkflow.specs import WorkflowSpec

class OpenWfeXmlSerializerTest(SerializerTest):
    CORRELATE = OpenWfeXmlSerializer

    def setUp(self):
        SerializerTest.setUp(self)
        self.serializer = OpenWfeXmlSerializer()
        self.serial_type = str

    def testConstructor(self):
        OpenWfeXmlSerializer()

    def testSerializeWorkflowSpec(self):
        pass # Serialization not yet supported.

    def testDeserializeWorkflowSpec(self):
        xml_file  = os.path.join(data_dir, 'openwfe', 'workflow1.xml')
        xml       = open(xml_file).read()
        path_file = os.path.splitext(xml_file)[0] + '.path'
        path      = open(path_file).read()
        wf_spec   = WorkflowSpec.deserialize(self.serializer, xml)

        run_workflow(self, wf_spec, path, None)

    def testSerializeWorkflow(self):
        pass # Serialization not yet supported.

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(OpenWfeXmlSerializerTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
