from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'neilc'


class NestedProcessesTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Nested*.bpmn20.xml', 
            'sid-a12cf1e5-86f4-4d69-9790-6a90342f5963')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):

        self.do_next_named_step('Action1')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.do_next_named_step('Action2')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.do_next_named_step('Action3')
        self.workflow.do_engine_steps()
        self.complete_subworkflow()
        self.complete_subworkflow()
        self.complete_subworkflow()
        self.save_restore()
        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

