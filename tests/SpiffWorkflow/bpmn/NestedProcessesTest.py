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

        self.complete_task('Action1', True)
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.complete_task('Action2', True)
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.complete_task('Action3', True)
        self.assertTrue(self.workflow.is_completed())

    def testResetToTop(self):

        self.complete_task('Action1', True)
        self.complete_task('Action2', True)
        self.complete_task('Action3', True)

        task = [t for t in self.workflow.get_tasks() if t.task_spec.bpmn_name == 'Action1'][0]
        self.workflow.reset_from_task_id(task.id)
        self.assertEqual(task.state, TaskState.READY)
        self.assertEqual(len(self.workflow.subprocesses), 0)
        task.run()

        self.complete_task('Action2')
        self.complete_task('Action3')
        self.assertTrue(self.workflow.is_completed())

    def testResetToIntermediate(self):

        self.complete_task('Action1', True)
        self.complete_task('Action2', True)
        self.complete_task('Action3', True)

        task = [t for t in self.workflow.get_tasks() if t.task_spec.bpmn_name == 'Action2'][0]
        sub = [t for t in self.workflow.get_tasks() if t.task_spec.bpmn_name == 'Nested level 1'][0]
        self.workflow.reset_from_task_id(task.id)
        self.assertEqual(task.state, TaskState.READY)
        self.assertEqual(sub.state, TaskState.WAITING)
        self.assertEqual(len(self.workflow.subprocesses), 1)
        task.run()

        self.complete_task('Action3')
        self.assertTrue(self.workflow.is_completed())

    def testResetToSubworkflow(self):

        self.complete_task('Action1', True)
        self.complete_task('Action2', True)
        self.complete_task('Action3', True)

        # "Nested level 1"
        task = self.workflow.get_tasks_from_spec_name('sid-C014B4B9-889F-4EE9-9949-C89502C35CF0')[0]
        self.workflow.reset_from_task_id(task.id)

        self.workflow.do_engine_steps()
        self.assertEqual(len(self.workflow.subprocesses), 1)
        self.assertEqual(task.state, TaskState.WAITING)
        self.complete_task('Action2', True)
        self.complete_task('Action3', True)
        self.assertTrue(self.workflow.is_completed())

    def complete_task(self, name, save_restore=False):
        self.do_next_named_step(name)
        self.workflow.do_engine_steps()
        #if save_restore:
        #    self.save_restore()
