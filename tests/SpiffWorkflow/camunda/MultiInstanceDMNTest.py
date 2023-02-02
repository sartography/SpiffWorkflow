import unittest

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import BoxedTaskDataEnvironment

from .BaseTestCase import BaseTestCase

class MultiInstanceDMNTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocesses = self.load_workflow_spec(
            'DMNMultiInstance.bpmn', 'Process_1', 'test_integer_decision_multi.dmn')
        self.workflow = BpmnWorkflow(self.spec)
        self.script_engine = PythonScriptEngine(environment=BoxedTaskDataEnvironment())
        self.workflow.script_engine = self.script_engine

    def testConstructor(self):
        pass  # this is accomplished through setup.

    def testDmnHappy(self):
        self.workflow.do_engine_steps()
        self.workflow.complete_next()
        self.workflow.do_engine_steps()
        self.workflow.complete_next()
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.data['stuff']['E']['y'], 'D')


    def testDmnSaveRestore(self):
        self.save_restore()
        self.workflow.script_engine = self.script_engine
        self.workflow.do_engine_steps()
        self.workflow.complete_next()
        self.save_restore()
        self.workflow.script_engine = self.script_engine
        self.workflow.do_engine_steps()
        self.workflow.complete_next()
        self.save_restore()
        self.workflow.script_engine = self.script_engine
        self.workflow.do_engine_steps()
        self.save_restore()
        self.workflow.script_engine = self.script_engine
        self.assertEqual(self.workflow.data['stuff']['E']['y'], 'D')



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MultiInstanceDMNTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
