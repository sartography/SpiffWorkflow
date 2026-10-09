"""Reproduce resetting a completed sequential multi-instance child.

With Python 3.10 or newer, install the checkout and run from its root:
    python -m pip install -e .
    python -m unittest -v tests.SpiffWorkflow.bpmn.SequentialMultiInstanceResetTest

Alternatively, use the repository's standard uv development environment:
    uv sync --extra dev
    uv run python -m unittest -v tests.SpiffWorkflow.bpmn.SequentialMultiInstanceResetTest

Expected current result: one passing forward control and two errors containing
"AttributeError: 'NoneType' object has no attribute 'append'". The command exits
with status 1 until the reset defect is fixed. No frontend, service connection,
credentials, or machine-specific interpreter path is required.

The plain BPMN fixture exports the loop's results through a data output
association. Forward execution works. Resetting the first completed child and
submitting a replacement output currently raises AttributeError in merge_child,
both in memory and after JSON serialization. These are deliberately failing
regression tests, not expectedFailure tests or assertions that the crash occurs.
"""

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase


class SequentialMultiInstanceResetTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('sequential_multiinstance_reset.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def complete_collection(self):
        first_id = None
        for expected_item in (1, 2):
            ready = self.get_ready_user_tasks()
            self.assertEqual(len(ready), 1)
            child = ready[0]
            self.assertEqual(child.task_spec.name, 'collect [child]')
            self.assertEqual(child.data['item'], expected_item)
            if first_id is None:
                first_id = child.id
            child.set_data(result=expected_item * 10)
            child.run()
            self.workflow.do_engine_steps()

        self.assertEqual(self.workflow.data_objects['results'], [10, 20])
        self.assertEqual([task.task_spec.name for task in self.get_ready_user_tasks()], ['review'])
        return first_id

    def testForwardExecution(self):
        self.complete_collection()
        self.get_ready_user_tasks()[0].run()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.completed)
        self.assertEqual(self.workflow.data_objects['results'], [10, 20])

    def testResetCompletedChild(self):
        self.reset_completed_child(save_restore=False)

    def testResetCompletedChildSaveRestore(self):
        self.reset_completed_child(save_restore=True)

    def reset_completed_child(self, save_restore):
        first_id = self.complete_collection()
        if save_restore:
            self.save_restore()

        # Repeated resets model backing up twice before submitting a new answer.
        # Use the public reset API; do not patch the parent accumulator or state.
        for _ in range(2):
            self.workflow.reset_from_task_id(first_id)
            self.workflow.do_engine_steps()
            if save_restore:
                self.save_restore()

        child = self.workflow.get_task_from_id(first_id)
        self.assertEqual(child.state, TaskState.READY)
        child.set_data(result=15)
        child.run()  # Currently fails: the completed parent no longer has results.
        self.workflow.do_engine_steps()

        # Allow later iterations to be replayed, but never duplicate a result or
        # leave more than one human task ready after the edited child completes.
        for _ in range(2):
            ready = self.get_ready_user_tasks()
            self.assertEqual(len(ready), 1)
            if ready[0].task_spec.name == 'review':
                break
            self.assertEqual(ready[0].task_spec.name, 'collect [child]')
            self.assertEqual(ready[0].data['item'], 2)
            ready[0].set_data(result=20)
            ready[0].run()
            self.workflow.do_engine_steps()

        self.assertEqual(self.workflow.data_objects['results'], [15, 20])
        self.assertEqual([task.task_spec.name for task in self.get_ready_user_tasks()], ['review'])
        self.get_ready_user_tasks()[0].run()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.completed)
        self.assertEqual(self.workflow.data_objects['results'], [15, 20])
