import os

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser, ValidationException
from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

class StandardLoopTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('standard_loop.bpmn','main', validate=False)
        # This spec has a loop task with loopMaximum = 3 and loopCondition = 'done'
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testLoopMaximum(self):

        start = self.workflow.get_tasks(end_at_spec='StartEvent_1')
        start[0].data['done'] = False
        for idx in range(3):
            self.workflow.do_engine_steps()
            self.workflow.refresh_waiting_tasks()
            ready_tasks = self.workflow.get_ready_user_tasks()
            self.assertEqual(len(ready_tasks), 1)
            ready_tasks[0].data[str(idx)] = True
            ready_tasks[0].run()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

    def testLoopCondition(self):

        start = self.workflow.get_tasks(end_at_spec='StartEvent_1')
        start[0].data['done'] = False

        self.workflow.do_engine_steps()
        self.workflow.refresh_waiting_tasks()
        ready_tasks = self.workflow.get_ready_user_tasks()
        self.assertEqual(len(ready_tasks), 1)
        ready_tasks[0].data['done'] = True
        ready_tasks[0].run()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

    def testSkipLoop(self):

        # This is called "skip loop" because I thought "testTestBefore" was a terrible name
        start = self.workflow.get_tasks(end_at_spec='StartEvent_1')
        start[0].data['done'] = True
        self.workflow.do_engine_steps()
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())


class ParseStandardLoop(BpmnWorkflowTestCase):

    def testParseStandardLoop(self):
        parser = BpmnParser()
        # This process has neither a loop condition nor a loop maximum
        bpmn_file = os.path.join(os.path.dirname(__file__), 'data', 'standard_loop_invalid.bpmn')
        parser.add_bpmn_file(bpmn_file)
        self.assertRaises(ValidationException, parser.get_spec, 'main')
