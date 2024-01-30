import unittest
import os
from datetime import datetime

from lxml import etree

from SpiffWorkflow import TaskState, Workflow
from SpiffWorkflow.specs import Cancel, Simple, WorkflowSpec
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
