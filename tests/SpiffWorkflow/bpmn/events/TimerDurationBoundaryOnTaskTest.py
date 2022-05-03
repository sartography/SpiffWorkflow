# -*- coding: utf-8 -*-



import unittest
import datetime
import time

from SpiffWorkflow.bpmn.FeelLikeScriptEngine import FeelLikeScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.specs.events import EndEvent
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
__author__ = 'kellym'


class TimerDurationTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('boundary_timer_on_task.bpmn', 'test_timer')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)


    def actual_test(self,save_restore = False):
        # In the normal flow of things, the final end event should be the last task
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(1, len(ready_tasks))
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        end_events = []

        for task in self.workflow.get_tasks():
            if isinstance(task.task_spec, EndEvent):
                end_events.append(task)
        self.assertEqual(1, len(end_events))

        # In the event of a timer firing, the last task should STILL
        # be the final end event.

        starttime = datetime.datetime.now()
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()
        time.sleep(0.5)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        task = self.workflow.get_ready_user_tasks()[0]
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()

        self.assertTrue(self.workflow.is_completed())
        end_events = []

        for task in self.workflow.get_tasks():
            if isinstance(task.task_spec, EndEvent):
                end_events.append(task)
        self.assertEqual(1, len(end_events))



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TimerDurationTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
