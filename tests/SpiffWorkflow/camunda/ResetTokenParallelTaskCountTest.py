from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase

__author__ = 'kellym'

class ResetTokenParallelTaskCountTest(BaseTestCase):
    """Assure that setting the token does not effect the overall task
    count. Added this when we discovered that this was growing
    exponentially in some cases.."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('token_trial_parallel_simple.bpmn', 'token_trial_parallel_simple')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testRunThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self, save_restore=False):
        total = 9

        # Set the workflow in motion, and assure we have the right
        # number of tasks

        self.workflow.do_engine_steps()
        self.assertEqual(total, len(self.workflow.get_tasks()))

        # Tell the exclusive gateway to skip the parallel tasks section.
        # We should still have the same number of tasks.
        data = {'skipParallel': True}
        task = self.get_ready_user_tasks()[0]
        task.data = data
        self.workflow.run_task_from_id(task.id)
        self.assertEquals(total, len(self.workflow.get_tasks()))

        # Reset the token to the first user task.
        # We should still have the same number of tasks.
        task.reset_token(data)
        self.assertEquals(total, len(self.workflow.get_tasks()))
        self.assertEquals(1, len(self.get_ready_user_tasks()))
