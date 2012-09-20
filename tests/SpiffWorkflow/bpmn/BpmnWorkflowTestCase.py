import os
import unittest
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnWorkflow
from SpiffWorkflow.bpmn.storage.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.bpmn.storage.MinimalistWorkflowSerializer import MinimalistWorkflowSerializer
from tests.SpiffWorkflow.bpmn.PackagerForTests import PackagerForTests

__author__ = 'matth'


class BpmnWorkflowTestCase(unittest.TestCase):

    def load_workflow_spec(self, filename, process_name):
        f = os.path.join(os.path.dirname(__file__), 'data', filename)

        return BpmnSerializer().deserialize_workflow_spec(
            PackagerForTests.package_in_memory(process_name, f))

    def do_next_exclusive_step(self, step_name, with_save_load=False, set_attribs=None, choice=None):
        if with_save_load:
            self.save_restore()

        self.workflow.do_engine_steps()
        tasks = self.workflow.get_tasks(Task.READY)
        self._do_single_step(step_name, tasks, set_attribs, choice)

    def do_next_named_step(self, step_name, with_save_load=False, set_attribs=None, choice=None):
        if with_save_load:
            self.save_restore()

        self.workflow.do_engine_steps()
        tasks = filter(lambda t: t.task_spec.name == step_name or t.task_spec.description == step_name, self.workflow.get_tasks(Task.READY))
        self._do_single_step(step_name, tasks, set_attribs, choice)

    def assertTaskNotReady(self, step_name):
        tasks = filter(lambda t: t.task_spec.name == step_name or t.task_spec.description == step_name, self.workflow.get_tasks(Task.READY))
        self.assertEquals([], tasks)

    def _do_single_step(self, step_name, tasks, set_attribs=None, choice=None):

        self.assertEqual(len(tasks), 1)

        self.assertTrue(tasks[0].task_spec.name == step_name or tasks[0].task_spec.description == step_name,
            'Expected step %s, got %s (%s)' % (step_name, tasks[0].task_spec.description, tasks[0].task_spec.name))
        if not set_attribs:
            set_attribs = {}

        if choice:
            set_attribs['choice'] = choice

        if set_attribs:
            tasks[0].set_attribute(**set_attribs)
        tasks[0].complete()

    def save_restore(self):
        state = self._get_workflow_state()
        self.restore(state)

    def restore(self, state):
        self.workflow = MinimalistWorkflowSerializer().deserialize_workflow(state, workflow_spec=self.spec)

    def get_read_only_workflow(self):
        state = self._get_workflow_state()
        return MinimalistWorkflowSerializer().deserialize_workflow(state, workflow_spec=self.spec, read_only=True)

    def _get_workflow_state(self):
        self.workflow.do_engine_steps()
        self.workflow.refresh_waiting_tasks()
        return MinimalistWorkflowSerializer().serialize_workflow(self.workflow, include_spec=False)
