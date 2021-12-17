# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import sys
import os
import unittest

from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class ResetSubProcessTest(BpmnWorkflowTestCase):
    """Assure we can reset a token to a previous task when we have
        a sub-workflow."""

    def setUp(self):
        self.filename = 'resetworkflowA-*.bpmn'
        self.process_name = 'TopLevel'
        self.spec = self.load_workflow1_spec()


    def reload_save_restore(self):
        self.filename = 'resetworkflowB-*.bpmn'
        self.spec = self.load_workflow1_spec()

        # Save and restore the workflow, without including the spec.
        # When loading the spec, use a slightly different spec.
        self.workflow.do_engine_steps()
        state = BpmnSerializer().serialize_workflow(self.workflow, include_spec=False)
        self.workflow = BpmnSerializer().deserialize_workflow(state, workflow_spec=self.spec)


    def load_workflow1_spec(self):
        return self.load_workflow_spec(self.filename, self.process_name)

    def testSaveRestore(self):
        self.actualTest(True)

    def testResetToOuterWorkflowWhileInSubWorkflow(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        top_level_task = self.workflow.get_ready_user_tasks()[0]
        self.workflow.complete_task_from_id(top_level_task.id)
        self.workflow.do_engine_steps()
        task = self.workflow.get_ready_user_tasks()[0]
        self.save_restore()
        top_level_task = self.workflow.get_tasks_from_spec_name('Task1')[0]
        top_level_task.reset_token(reset_data=True)
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task.get_name(), 'Task1')


    def actualTest(self, save_restore=False):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.assertEqual(1, len(self.workflow.get_ready_user_tasks()))
        task = self.workflow.get_ready_user_tasks()[0]
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        navlist = self.workflow.get_flat_nav_list()
        self.assertEqual(len(navlist),11)
        self.assertNav(navlist[5], name="SubTask2", state="READY")
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task.get_name(),'SubTask2')
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        task = self.workflow.get_tasks_from_spec_name('Task1')[0]
        task.reset_token()
        self.workflow.do_engine_steps()
        self.reload_save_restore()
        task = self.workflow.get_ready_user_tasks()[0]
        navlist = self.workflow.get_flat_nav_list()
        self.assertEqual(len(navlist), 12)
        self.assertNav(navlist[5], name="Subtask2", state=None)

        self.assertEqual(task.get_name(),'Task1')
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task.get_name(),'Subtask2')
        navlist = self.workflow.get_flat_nav_list()
        self.assertNav(navlist[5], name="Subtask2", state="READY")

        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task.get_name(),'Subtask2A')
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual(task.get_name(),'Task2')
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ResetSubProcessTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
