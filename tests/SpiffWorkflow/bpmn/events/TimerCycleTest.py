import datetime
import time

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment
from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'

counter = 0
def my_custom_function():
    global counter
    counter = counter+1
    return counter

class CustomScriptEngine(PythonScriptEngine):
    """This is a custom script processor that can be easily injected into Spiff Workflow.
    It will execute python code read in from the bpmn.  It will also make any scripts in the
     scripts directory available for execution. """
    def __init__(self):
        environment = TaskDataEnvironment({
            'custom_function': my_custom_function,
            'timedelta': datetime.timedelta,
        })
        super().__init__(environment=environment)



class TimerCycleTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('timer-cycle.bpmn', 'timer')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses, script_engine=CustomScriptEngine())

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):
        global counter
        counter = 0
        # See comments in timer cycle test start for more context
        for loopcount in range(4):
            self.workflow.do_engine_steps()
            if save_restore:
                self.save_restore()
            self.workflow.refresh_waiting_tasks()
            events = self.workflow.waiting_events()
            refill = self.workflow.get_tasks(spec_name='Refill_Coffee')
            # Wait time is 0.1s, with a limit of 2 children, so by the 3rd iteration, the event should be complete
            if loopcount < 2:
                self.assertEqual(len(events), 1)
            else:
                self.assertEqual(len(events), 0)
            # The first child should be created after one cycle has passed
            if loopcount == 0:
                self.assertEqual(len(refill), 0)
            time.sleep(0.1)

        # Get coffee still ready
        coffee = self.workflow.get_next_task(spec_name='Get_Coffee')
        self.assertEqual(coffee.state, TaskState.READY)
        # Timer completed
        timer = self.workflow.get_next_task(spec_name='CatchMessage')
        self.assertEqual(timer.state, TaskState.COMPLETED)
        self.assertEqual(counter, 2)
