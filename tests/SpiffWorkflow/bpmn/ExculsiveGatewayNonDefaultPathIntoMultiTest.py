# -*- coding: utf-8 -*-



import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class ExclusiveGatewayNonDefaultPathIntoMultiTest(BpmnWorkflowTestCase):
    """In the example BPMN Diagram we require that "Yes" or "No" be specified
    in a user task and check that a multiinstance can follow a non-default
    path.
    """

    def setUp(self):
        self.spec = self.load_workflow1_spec()

    def load_workflow1_spec(self):
        return self.load_workflow_spec('exclusive_non_default_path_into_multi.bpmn','ExclusiveNonDefaultMulti')

    def testRunThroughHappy(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        # Set initial array size to 3 in the first user form.
        task = self.workflow.get_ready_user_tasks()[0]
        self.assertEqual("DoStuff", task.task_spec.name)
        task.update_data({"morestuff": 'Yes'})
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()

        for i in range(3):
            task = self.workflow.get_ready_user_tasks()[0]
            if i == 0:
                self.assertEqual("GetMoreStuff", task.task_spec.name)
            else:
                self.assertEqual("GetMoreStuff_%d"%(i-1), task.task_spec.name)


            task.update_data({"stuff.addstuff": "Stuff %d"%i})
            self.workflow.complete_task_from_id(task.id)
            self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ExclusiveGatewayNonDefaultPathIntoMultiTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
