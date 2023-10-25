from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment

from .BaseTestCase import BaseTestCase

class MultiInstanceDMNTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocesses = self.load_workflow_spec(
            'DMNMultiInstance.bpmn', 'Process_1', 'test_integer_decision_multi.dmn')
        self.workflow = BpmnWorkflow(self.spec)
        self.script_engine = PythonScriptEngine(environment=TaskDataEnvironment())
        self.workflow.script_engine = self.script_engine

    def testDmnHappy(self):
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.data['stuff']['E']['y'], 'D')

    def testDmnSaveRestore(self):
        
        self.save_restore()
        self.workflow.do_engine_steps()
        self.workflow.run_next()
        self.save_restore()
        self.workflow.do_engine_steps()
        self.workflow.run_next()
        self.save_restore()
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertEqual(self.workflow.data['stuff']['E']['y'], 'D')
