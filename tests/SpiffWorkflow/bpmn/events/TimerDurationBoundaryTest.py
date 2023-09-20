import unittest
import time

from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase
__author__ = 'kellym'


class TimerDurationTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('boundary.bpmn', 'boundary_event')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(state=TaskState.READY)
        ready_tasks[0].run()
        self.workflow.do_engine_steps()

        loopcount = 0
        # test bpmn has a timeout of .03s; we should terminate loop before that.
        while len(self.workflow.get_tasks(state=TaskState.WAITING)) == 2 and loopcount < 11:
            if save_restore:
                self.save_restore()
            time.sleep(0.01)
            self.assertEqual(len(self.workflow.get_tasks(state=TaskState.READY)), 1)
            self.workflow.refresh_waiting_tasks()
            self.workflow.do_engine_steps()
            loopcount += 1

        self.workflow.do_engine_steps()
        subworkflow = self.workflow.get_next_task(spec_name='Subworkflow')
        self.assertEqual(subworkflow.state, TaskState.CANCELLED)
        ready_tasks = self.get_ready_user_tasks()
        while len(ready_tasks) > 0:
            ready_tasks[0].run()
            ready_tasks = self.get_ready_user_tasks()
            self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())
        # Assure that the loopcount is less than 10, and the timer interrupt fired, rather
        # than allowing us to continue to loop the full 10 times.
        self.assertTrue(loopcount < 10)
