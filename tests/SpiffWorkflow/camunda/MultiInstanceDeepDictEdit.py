# -*- coding: utf-8 -*-




import copy
import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
__author__ = 'matth'

from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase


class MultiInstanceDeepDictTest(BaseTestCase):
    """The example bpmn diagram tests both a set cardinality from user input
    as well as looping over an existing array."""

    deep_dict = {
        "StudyInfo": {
            "investigators": {
              "PI": {
                "affiliation": "",
                "department": "",
                "display_name": "Daniel Harold Funk",
                "email": "dhf8r@virginia.edu",
                "given_name": "Daniel",
                "sponsor_type": "Contractor",
                "telephone_number": "",
                "title": "",
                "type_full": "Primary Investigator",
                "user_id": "dhf8r"
              },
              "DC": {
                "type_full": "Department Contact",
                "user_id": "John Smith"
              }
            }
          }
        }

    expected_result = copy.copy(deep_dict)
    expected_result["StudyInfo"]["investigators"]["DC"]["email"] = "john.smith@gmail.com"
    expected_result["StudyInfo"]["investigators"]["PI"]["email"] = "dan.funk@gmail.com"

    def setUp(self):
        self.spec = self.load_workflow_spec(
            'data/multi_instance_parallel_deep_data_edit.bpmn',
            'MultiInstance')

    def testRunThroughHappy(self):
        self.actual_test(False)

    def testRunThroughSaveRestore(self):
        self.actual_test(True)

    def actual_test(self, save_restore=False):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        if save_restore: self.save_restore()

        # The initial task is a script task.  Set the data there
        # and move one.
        task = self.workflow.get_ready_user_tasks()[0]
        task.data = self.deep_dict
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        if save_restore: self.save_restore()

        task = self.workflow.get_ready_user_tasks()[0]
        taskinfo = task.task_info()
        self.assertEqual(taskinfo,{'is_looping':False,
                   'is_sequential_mi':False,
                   'is_parallel_mi':True,
                   'mi_count':2,
                   'mi_index':1})
        self.assertEqual("MultiInstanceTask", task.task_spec.name)
        self.assertTrue("investigator" in task.data)
        data = copy.copy(task.data)
        data['investigator']['email'] = "john.smith@gmail.com"
        task.update_data(data)
        self.workflow.complete_task_from_id(task.id)
        if save_restore: self.save_restore()


        task = self.workflow.get_ready_user_tasks()[0]
        taskinfo = task.task_info()
        self.assertEqual(taskinfo,{'is_looping':False,
                   'is_sequential_mi':False,
                   'is_parallel_mi':True,
                   'mi_count':2,
                   'mi_index':2})
        self.assertEqual("MultiInstanceTask", task.task_spec.name)
        self.assertTrue("investigator" in task.data)
        data = copy.copy(task.data)
        data['investigator']['email'] = "dan.funk@gmail.com"
        task.update_data(data)
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        if save_restore: self.save_restore()

        self.assertTrue(self.workflow.is_completed())
        task = self.workflow.last_task
        self.assertEqual(self.expected_result, task.data)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MultiInstanceDeepDictTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
