import unittest
import os
from datetime import datetime

from lxml import etree

from SpiffWorkflow import TaskState, Workflow
from SpiffWorkflow.specs.Cancel import Cancel
from SpiffWorkflow.specs.Simple import Simple
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from SpiffWorkflow.serializer.prettyxml import XmlSerializer

data_dir = os.path.join(os.path.dirname(__file__), 'data')

class IterationTest(unittest.TestCase):

    def setUp(self):
        xml_file = os.path.join(data_dir, 'iteration_test.xml')
        with open(xml_file) as fp:
            xml = etree.parse(fp).getroot()
        wf_spec = WorkflowSpec.deserialize(XmlSerializer(), xml)
        self.workflow = Workflow(wf_spec)

    def get_tasks_updated_after(self):
        start = self.workflow.get_next_task(end_at_spec='Start')
        start.run()
        updated = datetime.now().timestamp()
        for task in self.workflow.get_tasks(state=TaskState.READY):
            task.run()
        return updated

class DepthFirstTest(IterationTest):

    def test_get_tasks_updated_after(self):
        updated = super().get_tasks_updated_after()
        tasks = self.workflow.get_tasks(updated_ts=updated)
        self.assertListEqual(
            [t.task_spec.name for t in tasks],
            ['a', 'a1', 'a2', 'c', 'b', 'b1', 'b2']
        )

    def test_get_tasks_end_at(self):
        tasks = self.workflow.get_tasks(end_at_spec='c')
        self.assertEqual(
            [t.task_spec.name for t in tasks],
            ['Start', 'a', 'a1', 'last', 'End', 'a2', 'last', 'End', 'c', 'b', 'b1', 'last', 'End', 'b2', 'last', 'End']
        )

    def test_get_tasks_max_depth(self):
        tasks = self.workflow.get_tasks(max_depth=2)
        self.assertEqual(
            [t.task_spec.name for t in tasks],
            ['Start', 'a', 'a1', 'a2', 'c', 'b', 'b1', 'b2']
        )

class BreadthFirstTest(IterationTest):

    def test_get_tasks_updated_after(self):
        updated = super().get_tasks_updated_after()
        tasks = self.workflow.get_tasks(updated_ts=updated, depth_first=False)
        self.assertListEqual(
            [t.task_spec.name for t in tasks],
            ['a', 'b', 'a1', 'a2', 'c', 'b1', 'b2']
        )

    def test_get_tasks_end_at(self):
        tasks = self.workflow.get_tasks(end_at_spec='c', depth_first=False)
        self.assertEqual(
            [t.task_spec.name for t in tasks],
            ['Start', 'a', 'b', 'a1', 'a2', 'c', 'b1', 'b2', 'last', 'last', 'last', 'last', 'End', 'End', 'End', 'End']
        )

    def test_get_tasks_max_depth(self):
        tasks = self.workflow.get_tasks(max_depth=2, depth_first=False)
        self.assertEqual(
            [t.task_spec.name for t in tasks],
            ['Start', 'a', 'b', 'a1', 'a2', 'c', 'b1', 'b2']
        )
