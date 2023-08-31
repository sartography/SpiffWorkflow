import unittest
from unittest.mock import patch

from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase


class BusinessRuleTaskParserTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocesses = self.load_workflow_spec(
            'ExclusiveGatewayIfElseAndDecision.bpmn',
            'Process_1',
            'test_integer_decision.dmn')
        self.workflow = BpmnWorkflow(self.spec)

    def testDmnHappy(self):
        self.workflow.get_next_task(state=TaskState.READY).set_data(x=3)
        self.workflow.do_engine_steps()
        self.assertDictEqual(self.workflow.data, {'x': 3, 'y': 'A'})
        self.assertDictEqual(self.workflow.last_task.data, {'x': 3, 'y': 'A'})

    def testDmnSaveRestore(self):
        self.workflow.get_next_task(state=TaskState.READY).set_data(x=3)
        self.save_restore()
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertDictEqual(self.workflow.data, {'x': 3, 'y': 'A'})
        self.assertDictEqual(self.workflow.last_task.data, {'x': 3, 'y': 'A'})

    @patch('SpiffWorkflow.dmn.engine.DMNEngine.DMNEngine.evaluate')
    def testDmnExecHasAccessToTask(self, mock_engine):
        """At one time, the Execute and Evaluate methods received a Task object
        but the DMN evaluate method did not get a task object.  While this is
        an optional argument, it should always exist if executed in the context
        of a BPMNWorkflow"""
        self.workflow.get_next_task(state=TaskState.READY).set_data(x=3)
        self.workflow.do_engine_steps()
        task = self.workflow.get_next_task(spec_name='TaskDecision')
        name, args, kwargs = mock_engine.mock_calls[0]
        self.assertIn(task, args)

    def testDmnUsesSameScriptEngineAsBPMN(self):
        self.workflow.get_next_task(state=TaskState.READY).set_data(x=3)
        self.workflow.do_engine_steps()
