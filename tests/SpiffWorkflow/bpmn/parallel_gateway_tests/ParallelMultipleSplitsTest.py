from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class ParallelMultipleSplitsTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Multiple-Splits.bpmn20.xml',
            'sid-0f63def9-833d-4bcd-a6c4-8ef84a098b1a')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughAlternating(self):

        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Do First')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 1 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 2 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 3 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 1 - Yes Task')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 2 - Yes Task')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 3 - Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))
