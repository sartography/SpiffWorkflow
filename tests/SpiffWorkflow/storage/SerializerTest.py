# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import sys, unittest, re, os
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..'))

from PatternTest import run_workflow, PatternTest
from SpiffWorkflow.storage.Serializer import Serializer
from SpiffWorkflow.specs import WorkflowSpec
from SpiffWorkflow import Workflow
from SpiffWorkflow.storage.Exceptions import TaskSpecNotSupportedError, \
     TaskNotSupportedError
from data.spiff.workflow1 import TestWorkflowSpec

class SerializerTest(unittest.TestCase):
    CORRELATE = Serializer

    def setUp(self):
        self.wf_spec = TestWorkflowSpec()
        self.serializer = None
        self.serial_type = None

    def testConstructor(self):
        Serializer()

    def testSerializeWorkflowSpec(self, path_file=None, data=None):
        if self.serializer is None:
            return

        # Back to back testing.
        try:
            serialized1 = self.wf_spec.serialize(self.serializer)
            wf_spec     = WorkflowSpec.deserialize(self.serializer, serialized1)
            serialized2 = wf_spec.serialize(self.serializer)
        except TaskSpecNotSupportedError as e:
            pass
        else:
            self.assert_(isinstance(serialized1, self.serial_type))
            self.assert_(isinstance(serialized2, self.serial_type))
            self.compareSerialization(serialized1, serialized2)

            # Test whether the restored workflow still works.
            if path_file is None:
                path_file = os.path.join(data_dir, 'spiff', 'workflow1.path')
                path      = open(path_file).read()
            elif os.path.exists(path_file):
                path = open(path_file).read()
            else:
                path = None

            run_workflow(self, wf_spec, path, data)

    def compareSerialization(self, s1, s2):
        self.assertEqual(s1, s2)

    def testDeserializeWorkflowSpec(self):
        pass # Already covered in testSerializeWorkflowSpec()

    def testSerializeWorkflow(self, path_file=None, data=None):
        if self.serializer is None:
            return
        
        # Get a workflow, run it to completion, and see if it serialises and
        # deserialiases correctly.
        if path_file is None:
            path_file = os.path.join(data_dir, 'spiff', 'workflow1.path')
            path      = open(path_file).read()
        elif os.path.exists(path_file):
            path = open(path_file).read()
        else:
            path = None

            
        workflow  = run_workflow(self, self.wf_spec, path, data)

        # Back to back testing, as with wf_spec
        try:
            serialized1 = workflow.serialize(self.serializer)
            restored_wf = Workflow.deserialize(self.serializer, serialized1)
            serialized2 = restored_wf.serialize(self.serializer)
        except TaskNotSupportedError as e:
            pass
        else:
            self.assert_(isinstance(serialized1, self.serial_type))
            self.assert_(isinstance(serialized2, self.serial_type))
            self.compareSerialization(serialized1, serialized2)


    def testDeserializeWorkflow(self):
        pass # Already covered in testSerializeWorkflow()


class SerializeEveryPatternTest(PatternTest):
    def setUp(self):
        super(SerializeEveryPatternTest, self).setUp()
        self.serializerTestClass = SerializerTest(methodName='testConstructor')
        self.serializerTestClass.setUp()
        # we don't set self.serializer - that's set by the superclass to the
        # XML (de)serializer.

    def run_pattern(self, filename):
        # Load the .path file.
        path_file = os.path.splitext(filename)[0] + '.path'
        

        # Load the .data file.
        data_file = os.path.splitext(filename)[0] + '.data'
        if os.path.exists(data_file):
            expected_data = open(data_file, 'r').read()
        else:
            expected_data = None

        # Test patterns that are defined in XML format.
        if filename.endswith('.xml'):
            xml     = open(filename).read()
            wf_spec = WorkflowSpec.deserialize(self.serializer, xml, filename = filename)
            self.serializerTestClass.wf_spec = wf_spec
            self.serializerTestClass.testSerializeWorkflowSpec(path_file=path_file,
                                                               data=expected_data)
            self.serializerTestClass.testSerializeWorkflow(path_file=path_file,
                                                           data=expected_data)

        # Test patterns that are defined in Python.
        if filename.endswith('.py') and not filename.endswith('__.py'):
            code    = compile(open(filename).read(), filename, 'exec')
            thedict = {}
            result  = eval(code, thedict)
            wf_spec = thedict['TestWorkflowSpec']()
            self.serializerTestClass.wf_spec = wf_spec
            self.serializerTestClass.testSerializeWorkflowSpec(path_file=path_file,
                                                               data=expected_data)
            self.serializerTestClass.testSerializeWorkflow(path_file=path_file,
                                                           data=expected_data)

        
def suite():
    tests = unittest.defaultTestLoader.loadTestsFromTestCase(SerializerTest)
    # explicitly *don't* load the Every Pattern tester here - it creates lots of
    # totally useless output
    #tests.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(SerializeEveryPatternTest))
    return tests
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
