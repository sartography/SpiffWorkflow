from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase


class ParallelJoinInLoopTest(BpmnWorkflowTestCase):
    """A parallel join reached from two different splits, one of which is a loop back to it.

    On the first pass the manual branch of `initial_split` is empty, so it reaches the join
    immediately and the backbone branch arrives second. The join therefore fires on the backbone
    copy and cancels the manual copy. On the second pass, entered through `loop_split`, the
    backbone branch is the empty one, so the join must wait for `assess`.
    """

    def setUp(self):
        spec, subprocess_specs = self.load_workflow_spec('parallel_join_in_loop.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec, subprocess_specs)

    def completed_plan_tasks(self):
        return self.workflow.get_tasks(spec_name='plan', state=TaskState.COMPLETED)

    def test_join_waits_for_the_blocked_branch_on_a_later_iteration(self):
        self.workflow.do_engine_steps()

        # The second iteration cannot get past the join until `assess` is done, so the task after
        # the join must have run exactly once.
        self.assertEqual(1, len(self.completed_plan_tasks()))
        ready = self.workflow.get_tasks(state=TaskState.READY, manual=True)
        self.assertEqual(1, len(ready))
        self.assertEqual('assess', ready[0].task_spec.name)
        self.assertFalse(self.workflow.completed)

    def test_join_fires_once_per_iteration(self):
        self.workflow.do_engine_steps()
        for _ in range(3):
            ready = self.workflow.get_tasks(state=TaskState.READY, manual=True)
            if not ready:
                break
            self.save_restore()
            ready = self.workflow.get_tasks(state=TaskState.READY, manual=True)
            ready[0].run()
            self.workflow.do_engine_steps()

        # Three iterations of the loop, and the join must not let two tokens through on any of them.
        self.assertEqual(3, len(self.completed_plan_tasks()))
        self.assertTrue(self.workflow.completed)
        self.assertEqual(3, self.workflow.data['plan_runs'])
