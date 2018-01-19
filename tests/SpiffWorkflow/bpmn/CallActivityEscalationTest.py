# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
import datetime
import time
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kbogus@gmail.com'


def on_reached_cb(workflow, task, completed_set):
    # In workflows that load a subworkflow, the newly loaded children
    # will not have on_reached_cb() assigned. By using this function, we
    # re-assign the function in every step, thus making sure that new
    # children also call on_reached_cb().
    for child in task.children:
        track_task(child.task_spec, completed_set)
    return True


def on_complete_cb(workflow, task, completed_set):
    completed_set.add(task.task_spec.name)
    return True


def track_task(task_spec, completed_set):
    if task_spec.reached_event.is_connected(on_reached_cb):
        task_spec.reached_event.disconnect(on_reached_cb)
    task_spec.reached_event.connect(on_reached_cb, completed_set)
    if task_spec.completed_event.is_connected(on_complete_cb):
        task_spec.completed_event.disconnect(on_complete_cb)
    task_spec.completed_event.connect(on_complete_cb, completed_set)


def track_workflow(wf_spec, completed_set):
    for name in wf_spec.task_specs:
        track_task(wf_spec.task_specs[name], completed_set)


class CallActivityEscalationTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/*.bpmn20.xml', 'CallActivity-Escalation-Test')

    def testShouldEscalate(self):
        completed_set = set()
        track_workflow(self.spec, completed_set)
        self.workflow = BpmnWorkflow(self.spec)
        for task in self.workflow.get_tasks(Task.READY):
            task.set_data(should_escalate=True)
        self.workflow.complete_all()
        self.assertEqual(True, self.workflow.is_completed())

        self.assertEqual(True, 'EndEvent_specific1_noninterrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_specific1_noninterrupting_escalated' in completed_set)

        self.assertEqual(True, 'EndEvent_specific1_interrupting_normal' not in completed_set)
        self.assertEqual(True, 'EndEvent_specific1_interrupting_escalated' in completed_set)

        self.assertEqual(True, 'EndEvent_specific2_noninterrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_noninterrupting_escalated' in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_noninterrupting_missingvariable' not in completed_set)

        self.assertEqual(True, 'EndEvent_specific2_interrupting_normal' not in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_interrupting_escalated' in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_interrupting_missingvariable' not in completed_set)

        self.assertEqual(True, 'EndEvent_general_noninterrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_general_noninterrupting_escalated' in completed_set)

        self.assertEqual(True, 'EndEvent_general_interrupting_normal' not in completed_set)
        self.assertEqual(True, 'EndEvent_general_interrupting_escalated' in completed_set)

    def testShouldNotEscalate(self):
        completed_set = set()
        track_workflow(self.spec, completed_set)
        self.workflow = BpmnWorkflow(self.spec)
        for task in self.workflow.get_tasks(Task.READY):
            task.set_data(should_escalate=False)
        self.workflow.complete_all()
        self.assertEqual(True, self.workflow.is_completed())

        self.assertEqual(True, 'EndEvent_specific1_noninterrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_specific1_noninterrupting_escalated' not in completed_set)

        self.assertEqual(True, 'EndEvent_specific1_interrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_specific1_interrupting_escalated' not in completed_set)

        self.assertEqual(True, 'EndEvent_specific2_noninterrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_noninterrupting_escalated' not in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_noninterrupting_missingvariable' not in completed_set)

        self.assertEqual(True, 'EndEvent_specific2_interrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_interrupting_escalated' not in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_interrupting_missingvariable' not in completed_set)

        self.assertEqual(True, 'EndEvent_general_noninterrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_general_noninterrupting_escalated' not in completed_set)

        self.assertEqual(True, 'EndEvent_general_interrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_general_interrupting_escalated' not in completed_set)

    def testMissingVariable(self):
        completed_set = set()
        track_workflow(self.spec, completed_set)
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.complete_all()
        self.assertEqual(True, self.workflow.is_completed())

        self.assertEqual(True, 'EndEvent_specific1_noninterrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_specific1_noninterrupting_escalated' not in completed_set)

        self.assertEqual(True, 'EndEvent_specific1_interrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_specific1_interrupting_escalated' not in completed_set)

        self.assertEqual(True, 'EndEvent_specific2_noninterrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_noninterrupting_escalated' not in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_noninterrupting_missingvariable' in completed_set)

        self.assertEqual(True, 'EndEvent_specific2_interrupting_normal' not in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_interrupting_escalated' not in completed_set)
        self.assertEqual(True, 'EndEvent_specific2_interrupting_missingvariable' in completed_set)

        self.assertEqual(True, 'EndEvent_general_noninterrupting_normal' in completed_set)
        self.assertEqual(True, 'EndEvent_general_noninterrupting_escalated' in completed_set)

        self.assertEqual(True, 'EndEvent_general_interrupting_normal' not in completed_set)
        self.assertEqual(True, 'EndEvent_general_interrupting_escalated' in completed_set)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CallActivityEscalationTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
