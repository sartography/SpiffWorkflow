# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'

from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase


class SubWorkflowTest(BaseTestCase):
    """The tests a somewhat complex subworkflow and verifies that it does
       what we expect"""

    def setUp(self):
        self.spec = self.load_workflow_spec(
            'data/subWorkflowComplex.bpmn',
            'SubWorkflow')
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.answers = ['A','A1','A2','B']

    def testRunThroughHappy(self):
        self.actual_test(False)

    def testRunThroughSaveRestore(self):
        self.actual_test(True)

    def actual_test(self, save_restore=False):


        # Set initial array size to 3 in the first user form.
        for answer in self.answers:
            task = self.workflow.get_ready_user_tasks()[0]
            self.assertEqual("Activity_"+answer, task.task_spec.name)
            task.update_data({"Field"+answer: answer})
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        self.assertEqual(self.workflow.last_task.data,{'FieldA': 'A',
                                                        'FieldA1': 'A1',
                                                        'FieldA2': 'A2',
                                                        'FieldB': 'B'})
        self.assertTrue(self.workflow.is_completed())

    def testSubWorkflowNav(self):
        flat = self.workflow.get_flat_nav_list()
        nav = self.workflow.get_deep_nav_list()
        self.assertNav(nav[0], spec_type="StartEvent")
        self.assertNav(nav[1], spec_type="CallActivity", state="READY")
        self.assertNav(nav[1].children[0], spec_type="StartEvent", state="COMPLETED")
        self.assertNav(nav[1].children[1], description="FormA", state="READY")
        self.assertNav(nav[1].children[2], spec_type="ParallelGateway")
        self.assertNav(nav[1].children[2].children[0], description="Form A1")
        self.assertNav(nav[1].children[2].children[1], description="Form A2")
        self.assertNav(nav[1].children[4], spec_type="EndEvent")
        self.assertNav(nav[2], spec_type="UserTask", description="FormB", state="FUTURE")
        self.assertNav(nav[3], spec_type="EndEvent", state="FUTURE")


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SubWorkflowTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
