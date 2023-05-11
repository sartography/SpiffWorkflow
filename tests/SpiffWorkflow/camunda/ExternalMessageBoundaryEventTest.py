# -*- coding: utf-8 -*-
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.camunda.specs.event_definitions import MessageEventDefinition
from .BaseTestCase import BaseTestCase

__author__ = 'kellym'


class ExternalMessageBoundaryTest(BaseTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('external_message.bpmn', 'Process_1iggtmi')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)


    def actual_test(self,save_restore = False):

        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(1, len(ready_tasks),'Expected to have only one ready task')
        self.workflow.catch(MessageEventDefinition('Interrupt', payload='SomethingImportant', result_var='interrupt_var'))
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(2,len(ready_tasks),'Expected to have two ready tasks')

        # here because the thread just dies and doesn't lead to a task, we expect the data
        # to die with it.
        # item 1 should be at 'Pause'
        self.assertEqual('Pause',ready_tasks[1].task_spec.bpmn_name)
        self.assertEqual('SomethingImportant', ready_tasks[1].data['interrupt_var'])
        self.assertEqual(True, ready_tasks[1].data['caughtinterrupt'])
        self.assertEqual('Meaningless User Task',ready_tasks[0].task_spec.bpmn_name)
        self.assertEqual(False, ready_tasks[0].data['caughtinterrupt'])
        ready_tasks[1].run()
        self.workflow.do_engine_steps()
        # what I think is going on here is that when we hit the reset, it is updating the
        # last_task and appending the data to whatever happened there, so it would make sense that
        # we have the extra variables that happened in 'pause'
        # if on the other hand, we went on from 'meaningless task' those variables would not get added.
        self.workflow.catch(MessageEventDefinition('reset', payload='SomethingDrastic', result_var='reset_var'))
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        # The user activity was cancelled and we should continue from the boundary event
        self.assertEqual(2, len(ready_tasks), 'Expected to have two ready tasks')
        event = self.workflow.get_tasks_from_spec_name('Event_19detfv')[0]
        event.run()
        self.assertEqual('SomethingDrastic', event.data['reset_var'])
        self.assertEqual(False, event.data['caughtinterrupt'])
