import unittest
import os

from lxml import etree

from SpiffWorkflow import TaskState, Workflow
from SpiffWorkflow.exceptions import TaskNotFoundException
from SpiffWorkflow.specs import Simple, WorkflowSpec
from SpiffWorkflow.serializer.prettyxml import XmlSerializer

data_dir = os.path.join(os.path.dirname(__file__), 'data')

class WorkflowTest(unittest.TestCase):

    def setUp(self):
        xml_file = os.path.join(data_dir, 'workflow1.xml')
        with open(xml_file) as fp:
            xml = etree.parse(fp).getroot()
        wf_spec = WorkflowSpec.deserialize(XmlSerializer(), xml)
        self.workflow = Workflow(wf_spec)

    def test_interactive_calls(self):
        """Simulates interactive calls, as would be issued by a user."""

        tasks = self.workflow.get_tasks(state=TaskState.READY)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_spec.name, 'Start')
        self.workflow.run_task_from_id(tasks[0].id)
        self.assertEqual(tasks[0].state, TaskState.COMPLETED)

        tasks = self.workflow.get_tasks(state=TaskState.READY)
        self.assertEqual(len(tasks), 2)
        task_a1 = tasks[0]
        task_b1 = tasks[1]
        self.assertEqual(task_a1.task_spec.__class__, Simple)
        self.assertEqual(task_a1.task_spec.name, 'task_a1')
        self.assertEqual(task_b1.task_spec.__class__, Simple)
        self.assertEqual(task_b1.task_spec.name, 'task_b1')
        self.workflow.run_task_from_id(task_a1.id)
        self.assertEqual(task_a1.state, TaskState.COMPLETED)

        tasks = self.workflow.get_tasks(state=TaskState.READY)
        self.assertEqual(len(tasks), 2)
        self.assertTrue(task_b1 in tasks)
        task_a2 = tasks[0]
        self.assertEqual(task_a2.task_spec.__class__, Simple)
        self.assertEqual(task_a2.task_spec.name, 'task_a2')
        self.workflow.run_task_from_id(task_a2.id)

        tasks = self.workflow.get_tasks(state=TaskState.READY)
        self.assertEqual(len(tasks), 1)
        self.assertTrue(task_b1 in tasks)

        self.workflow.run_task_from_id(task_b1.id)
        tasks = self.workflow.get_tasks(state=TaskState.READY)
        self.assertEqual(len(tasks), 1)
        self.workflow.run_task_from_id(tasks[0].id)

        tasks = self.workflow.get_tasks(state=TaskState.READY)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_spec.name, 'synch_1')

    def test_task_removed_event(self):
        removed_tasks = []

        def task_removed(workflow, task):
            self.assertIs(workflow, self.workflow)
            with self.assertRaises(TaskNotFoundException):
                workflow.get_task_from_id(task.id)
            self.assertNotIn(task, task.parent.children)
            removed_tasks.append(task)

        self.workflow.task_removed_event.connect(task_removed)
        task = self.workflow.get_next_task(spec_name='task_c1')
        self.workflow._remove_task(task.id)

        self.assertEqual(
            [removed_task.task_spec.name for removed_task in removed_tasks],
            ['excl_choice_2', 'task_c1'],
        )
