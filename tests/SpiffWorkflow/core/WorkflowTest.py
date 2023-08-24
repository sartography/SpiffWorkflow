import unittest
import os
from datetime import datetime

from lxml import etree

from SpiffWorkflow.workflow import Workflow
from SpiffWorkflow.specs.Cancel import Cancel
from SpiffWorkflow.specs.Simple import Simple
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from SpiffWorkflow.task import TaskState, TaskIterator
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

        tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_spec.name, 'Start')
        self.workflow.run_task_from_id(tasks[0].id)
        self.assertEqual(tasks[0].state, TaskState.COMPLETED)

        tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 2)
        task_a1 = tasks[0]
        task_b1 = tasks[1]
        self.assertEqual(task_a1.task_spec.__class__, Simple)
        self.assertEqual(task_a1.task_spec.name, 'task_a1')
        self.assertEqual(task_b1.task_spec.__class__, Simple)
        self.assertEqual(task_b1.task_spec.name, 'task_b1')
        self.workflow.run_task_from_id(task_a1.id)
        self.assertEqual(task_a1.state, TaskState.COMPLETED)

        tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 2)
        self.assertTrue(task_b1 in tasks)
        task_a2 = tasks[0]
        self.assertEqual(task_a2.task_spec.__class__, Simple)
        self.assertEqual(task_a2.task_spec.name, 'task_a2')
        self.workflow.run_task_from_id(task_a2.id)

        tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 1)
        self.assertTrue(task_b1 in tasks)

        self.workflow.run_task_from_id(task_b1.id)
        tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 1)
        self.workflow.run_task_from_id(tasks[0].id)

        tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_spec.name, 'synch_1')

    def test_get_tasks_updated_after(self):

        start = self.workflow.get_tasks_from_spec_name('Start')[0]
        start.run()
        updated = datetime.now().timestamp()
        ready = self.workflow.get_tasks(TaskState.READY)
        for task in self.workflow.get_tasks(state=TaskState.READY):
            task.run()
        tasks = self.workflow.get_tasks(updated_after=updated)
        self.assertListEqual([t.task_spec.name for t in tasks], ['task_a1', 'task_a2', 'task_b1', 'task_b2'])

    def test_get_tasks_end_at(self):

        tasks = self.workflow.get_tasks(end_at='excl_choice_1')
        spec_names = [t.task_spec.name for t in tasks]
        self.assertEqual(len([name for name in spec_names if name == 'excl_choice_1']), 2)
        self.assertNotIn('task_c1', spec_names)
        self.assertNotIn('task_c2', spec_names)
        self.assertNotIn('task_c3', spec_names)

    def test_get_tasks_max_depth(self):
        tasks = [t for t in self.workflow.get_tasks(max_depth=2)]
        self.assertListEqual([t.task_spec.name for t in tasks], ['Start', 'task_a1', 'task_a2', 'task_b1', 'task_b2'])
