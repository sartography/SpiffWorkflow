from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class ParallelJoinLongInclusiveTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Join-Long-Inclusive.bpmn20.xml',
            'sid-bae04828-c969-4480-8cfe-09ad1f97d81c')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughThread1FirstThenNo(self):

        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Thread 1 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        for i in range(1, 13):
            self.do_next_named_step('Thread 1 - Task %d' % i)
            self.workflow.do_engine_steps()

        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.assertEqual(1, len(self.workflow.get_tasks(task_filter=self.waiting_task_filter)))

        self.do_next_named_step('Thread 2 - Choose', choice='No', with_save_load=True)
        self.workflow.do_engine_steps()
        self.do_next_named_step('Done', with_save_load=True)
        self.workflow.do_engine_steps()
        self.do_next_named_step('Thread 2 - No Task', with_save_load=True)
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))

    def testNoFirstThenThread1(self):

        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Thread 2 - Choose', choice='No', with_save_load=True)
        self.workflow.do_engine_steps()

        self.do_next_named_step('Thread 1 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        for i in range(1, 13):
            self.do_next_named_step('Thread 1 - Task %d' % i)
            self.workflow.do_engine_steps()

        self.do_next_named_step('Done', with_save_load=True)
        self.workflow.do_engine_steps()

        self.do_next_named_step('Thread 2 - No Task', with_save_load=True)
        self.workflow.do_engine_steps()

        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))
