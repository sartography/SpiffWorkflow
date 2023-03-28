# -*- coding: utf-8 -*-

import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase

__author__ = 'kellym'


class SubWorkflowTest(BaseTestCase):
    """The tests a somewhat complex subworkflow and verifies that it does
       what we expect"""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('subWorkflowComplex.bpmn', 'SubWorkflow')
        self.workflow = BpmnWorkflow(spec, subprocesses)
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
            self.workflow.run_task_from_id(task.id)
            self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        self.assertEqual(self.workflow.last_task.data,{'FieldA': 'A',
                                                        'FieldA1': 'A1',
                                                        'FieldA2': 'A2',
                                                        'FieldB': 'B'})
        self.assertTrue(self.workflow.is_completed())

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(SubWorkflowTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
