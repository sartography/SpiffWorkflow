# -*- coding: utf-8 -*-



import unittest
import datetime
import time
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'kellym'


class NIMessageBoundaryTest(BpmnWorkflowTestCase):
    """
    Non-Interrupting Timer boundary test
    """
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('noninterrupting-MessageBoundary.bpmn', 'MessageBoundary')

    def testRunThroughHappy(self):
        self.actual_test(save_restore=False)

    def testThroughSaveRestore(self):
        self.actual_test(save_restore=True)


    def actual_test(self,save_restore = False):
        self.workflow = BpmnWorkflow(self.spec)
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEqual(1, len(ready_tasks))
        self.workflow.complete_task_from_id(ready_tasks[0].id)
        self.workflow.do_engine_steps()

        # first we run through a couple of steps where we answer No to each
        # question
        answers = {'Activity_WorkLate':('flag_task','No'),
                   'Activity_DoWork': ('work_done','No')}
        for x in range(3):
            ready_tasks = self.workflow.get_tasks(Task.READY)
            for task in ready_tasks:
                response = answers.get(task.task_spec.name,None)
                self.assertEqual(response==None,
                                 False,
                                 'We got a ready task that we did not expect - %s'%(
                                 task.task_spec.name))
                task.data[response[0]] = response[1]
                self.workflow.complete_task_from_id(task.id)
                self.workflow.do_engine_steps()
            # if we have a list of tasks - that list becomes invalid
            # after we do a save restore, so I'm completing the list
            # before doing the save restore.
            if save_restore: self.save_restore()


        answers = {'Activity_WorkLate':('flag_task','Yes'),
                   'Activity_DoWork': ('work_done','No'),
                   'Activity_WorkLateReason':('work_late_reason','covid-19')}
        for x in range(3):
            ready_tasks = self.workflow.get_tasks(Task.READY)
            for task in ready_tasks:
                response = answers.get(task.task_spec.name,None)
                self.assertEqual(response==None,
                                 False,
                                 'We got a ready task that we did not expect - %s'%(
                                 task.task_spec.name))
                task.data[response[0]] = response[1]
                self.workflow.complete_task_from_id(task.id)
                self.workflow.do_engine_steps()
            if save_restore: self.save_restore()

        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEqual(len(ready_tasks),1)
        task = ready_tasks[0]
        self.assertEqual(task.task_spec.name,'Activity_DoWork')
        task.data['work_done'] = 'Yes'
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEqual(len(ready_tasks), 1)
        task = ready_tasks[0]
        self.assertEqual(task.task_spec.name, 'Activity_WorkCompleted')
        task.data['work_completed'] = 'Lots of Stuff'
        self.workflow.complete_task_from_id(task.id)
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.is_completed(),True)
        self.assertEqual(self.workflow.last_task.data,{'Event_InterruptBoundary_Response': 'Youre late!',
                                                       'flag_task': 'Yes',
                                                       'work_done': 'Yes',
                                                       'work_completed': 'Lots of Stuff',
                                                       'work_late_reason': 'covid-19'})


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(NIMessageBoundaryTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
