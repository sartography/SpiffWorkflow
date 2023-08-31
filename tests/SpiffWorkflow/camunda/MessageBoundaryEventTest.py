import time
from datetime import timedelta
from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment
from .BaseTestCase import BaseTestCase

__author__ = 'kellym'


class MessageBoundaryTest(BaseTestCase):

    def setUp(self):
        self.script_engine = PythonScriptEngine(environment=TaskDataEnvironment({"timedelta": timedelta}))
        self.spec, self.subprocesses = self.load_workflow_spec('MessageBoundary.bpmn', 'Process_1kjyavs')
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses, script_engine=self.script_engine)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)

    def actual_test(self,save_restore = False):
        steps = [('Activity_Interrupt', {'interrupt_task':'No'}),
                 ('Activity_Interrupt', {'interrupt_task': 'No'}),
                 ('Activity_Interrupt', {'interrupt_task': 'Yes'}),
                 ]
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(state=TaskState.READY)
        self.assertEqual(2, len(ready_tasks),'Expected to have two ready tasks')
        for step in steps:
            for task in ready_tasks:
                if task.task_spec.name == step[0]:
                    task.update_data(step[1])

                self.workflow.run_task_from_id(task.id)
                self.workflow.do_engine_steps()
                time.sleep(.01)
                self.workflow.refresh_waiting_tasks()
                if save_restore:
                    self.save_restore()
                    self.workflow.script_engine = self.script_engine
            ready_tasks = self.workflow.get_tasks(state=TaskState.READY)
        time.sleep(.01)
        self.workflow.refresh_waiting_tasks()
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.is_completed(), True, 'Expected the workflow to be complete at this point')

