# -*- coding: utf-8 -*-

import unittest
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'michaelc'


class TransactionSubprocessTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('transaction.bpmn', 'Main_Process')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        self.workflow.do_engine_steps()

    def testNormalCompletion(self):

        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        ready_tasks[0].update_data({'value': 'asdf'})
        ready_tasks[0].run()
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        ready_tasks[0].update_data({'quantity': 2})
        ready_tasks[0].run()
        self.workflow.do_engine_steps()
        self.assertIn('value', self.workflow.last_task.data)

        # Check that workflow and next task completed
        subprocess = self.workflow.get_tasks_from_spec_name('Subprocess')[0]
        self.assertEqual(subprocess.state, TaskState.COMPLETED)
        print_task = self.workflow.get_tasks_from_spec_name("Activity_Print_Data")[0]
        self.assertEqual(print_task.state, TaskState.COMPLETED)

        # Check that the boundary events were cancelled
        cancel_task = self.workflow.get_tasks_from_spec_name("Catch_Cancel_Event")[0]
        self.assertEqual(cancel_task.state, TaskState.CANCELLED)
        error_1_task = self.workflow.get_tasks_from_spec_name("Catch_Error_1")[0]
        self.assertEqual(error_1_task.state, TaskState.CANCELLED)
        error_none_task = self.workflow.get_tasks_from_spec_name("Catch_Error_None")[0]
        self.assertEqual(error_none_task.state, TaskState.CANCELLED)


    def testSubworkflowCancelEvent(self):

        ready_tasks = self.workflow.get_tasks(TaskState.READY)

        # If value == '', we cancel
        ready_tasks[0].update_data({'value': ''})
        ready_tasks[0].run()
        self.workflow.do_engine_steps()

        # If the subprocess gets cancelled, verify that data set there does not persist
        self.assertNotIn('value', self.workflow.last_task.data)

        # Check that we completed the Cancel Task
        cancel_task = self.workflow.get_tasks_from_spec_name("Cancel_Action")[0]
        self.assertEqual(cancel_task.state, TaskState.COMPLETED)

        # And cancelled the remaining tasks
        error_1_task = self.workflow.get_tasks_from_spec_name("Catch_Error_1")[0]
        self.assertEqual(error_1_task.state, TaskState.CANCELLED)
        error_none_task = self.workflow.get_tasks_from_spec_name("Catch_Error_None")[0]
        self.assertEqual(error_none_task.state, TaskState.CANCELLED)

        # We should not have this task, as we followed the 'cancel branch'
        print_task = self.workflow.get_tasks_from_spec_name("Activity_Print_Data")
        self.assertEqual(len(print_task), 0)

    def testSubworkflowErrorCodeNone(self):

        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        ready_tasks[0].update_data({'value': 'asdf'})
        ready_tasks[0].run()
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)

        # If quantity == 0, we throw an error with no error code
        ready_tasks[0].update_data({'quantity': 0})
        ready_tasks[0].run()
        self.workflow.do_engine_steps()

        # We formerly checked that subprocess data does not persist, but I think it should persist
        # A boundary event is just an alternate path out of a workflow, and we might need the context
        # of the event in later steps

        # The cancel boundary event should be cancelled
        cancel_task = self.workflow.get_tasks_from_spec_name("Catch_Cancel_Event")[0]
        self.assertEqual(cancel_task.state, TaskState.CANCELLED)

        # We should catch the None Error, but not Error 1
        error_none_task = self.workflow.get_tasks_from_spec_name("Catch_Error_None")[0]
        self.assertEqual(error_none_task.state, TaskState.COMPLETED)
        error_1_task = self.workflow.get_tasks_from_spec_name("Catch_Error_1")[0]
        self.assertEqual(error_1_task.state, TaskState.CANCELLED)

        # Make sure this branch didn't getfollowed
        print_task = self.workflow.get_tasks_from_spec_name("Activity_Print_Data")
        self.assertEqual(len(print_task), 0)

    def testSubworkflowErrorCodeOne(self):

        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        ready_tasks[0].update_data({'value': 'asdf'})
        ready_tasks[0].run()
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)

        # If quantity < 0, we throw 'Error 1'
        ready_tasks[0].update_data({'quantity': -1})
        ready_tasks[0].run()
        self.workflow.do_engine_steps()

        # The cancel boundary event should be cancelled
        # I've removed this check, see previous test for rationale

        # Both boundary events should complete
        error_none_task = self.workflow.get_tasks_from_spec_name("Catch_Error_None")[0]
        self.assertEqual(error_none_task.state, TaskState.COMPLETED)
        error_1_task = self.workflow.get_tasks_from_spec_name("Catch_Error_1")[0]
        self.assertEqual(error_1_task.state, TaskState.COMPLETED)

        print_task = self.workflow.get_tasks_from_spec_name("Activity_Print_Data")
        self.assertEqual(len(print_task), 0)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TransactionSubprocessTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
