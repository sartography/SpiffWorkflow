# -*- coding: utf-8 -*-

import sys
import unittest
import os
data_dir = os.path.join(os.path.dirname(__file__), 'data')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from SpiffWorkflow import Workflow
from SpiffWorkflow.specs import *
from SpiffWorkflow.operators import *
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.serializer.prettyxml import XmlSerializer


class WorkflowTest(unittest.TestCase):

    def testConstructor(self):
        wf_spec = WorkflowSpec()
        wf_spec.start.connect(Cancel(wf_spec, 'name'))
        workflow = Workflow(wf_spec)

    def testBeginWorkflowStepByStep(self):
        """
        Simulates interactive calls, as would be issued by a user.
        """
        xml_file = os.path.join(data_dir, 'spiff', 'workflow1.xml')
        with open(xml_file) as fp:
            xml = fp.read()
        wf_spec = WorkflowSpec.deserialize(XmlSerializer(), xml)
        workflow = Workflow(wf_spec)

        tasks = workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_spec.name, 'Start')
        workflow.complete_task_from_id(tasks[0].id)
        self.assertEqual(tasks[0].state, TaskState.COMPLETED)

        tasks = workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 2)
        task_a1 = tasks[0]
        task_b1 = tasks[1]
        self.assertEqual(task_a1.task_spec.__class__, Simple)
        self.assertEqual(task_a1.task_spec.name, 'task_a1')
        self.assertEqual(task_b1.task_spec.__class__, Simple)
        self.assertEqual(task_b1.task_spec.name, 'task_b1')
        workflow.complete_task_from_id(task_a1.id)
        self.assertEqual(task_a1.state, TaskState.COMPLETED)

        tasks = workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 2)
        self.assertTrue(task_b1 in tasks)
        task_a2 = tasks[0]
        self.assertEqual(task_a2.task_spec.__class__, Simple)
        self.assertEqual(task_a2.task_spec.name, 'task_a2')
        workflow.complete_task_from_id(task_a2.id)

        tasks = workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 1)
        self.assertTrue(task_b1 in tasks)

        workflow.complete_task_from_id(task_b1.id)
        tasks = workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 1)
        workflow.complete_task_from_id(tasks[0].id)

        tasks = workflow.get_tasks(TaskState.READY)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_spec.name, 'synch_1')
        # haven't reached the end of the workflow, but stopping at "synch_1"


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(WorkflowTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
