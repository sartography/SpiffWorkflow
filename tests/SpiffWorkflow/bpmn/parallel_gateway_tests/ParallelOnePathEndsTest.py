from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class ParallelOnePathEndsTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-One-Path-Ends.bpmn20.xml',
            'sid-33b2dda8-ca46-47ca-9f08-43de73abde9e')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughParallelTaskFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(state=TaskState.READY)))

        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='No')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(0, len(self.workflow.get_tasks(state=TaskState.READY|TaskState.WAITING)))

    def testRunThroughChoiceFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(state=TaskState.READY)))

        self.do_next_named_step('Choice 1', choice='No')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(0, len(self.workflow.get_tasks(state=TaskState.READY|TaskState.WAITING)))

    def testRunThroughParallelTaskFirstYes(self):

        self.assertEqual(2, len(self.workflow.get_tasks(state=TaskState.READY)))

        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(0, len(self.workflow.get_tasks(state=TaskState.READY|TaskState.WAITING)))
