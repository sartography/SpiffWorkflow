from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class ParallelThenExclusiveTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Then-Exclusive.bpmn20.xml',
            'sid-bb9ea2d5-58b6-43c7-8e77-6e28f71106f0')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughParallelTaskFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))

    def testRunThroughChoiceFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))

    def testRunThroughChoiceThreadCompleteFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(task_filter=self.ready_task_filter)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(0, len(self.workflow.get_tasks(task_filter=self.ready_or_waiting_filter)))


class ParallelThenExclusiveNoInclusiveTest(ParallelThenExclusiveTest):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Then-Exclusive-No-Inclusive.bpmn20.xml', 
            'sid-900d26c9-beab-47a4-8092-4284bfb39927')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()


