# -*- coding: utf-8 -*-

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

class ParallelThroughSameTaskTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Through-Same-Task.bpmn20.xml',
            'sid-57c563e3-fb68-4961-ae34-b6201e0c09e8')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughFirstRepeatTaskFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()
        # The inclusive gateway allows this to pass through (since there is a
        # route to it on the same sequence flow)
        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRepeatTasksReadyTogether(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(2, len(ready_tasks))
        self.assertEqual(
            'Repeated Task', ready_tasks[0].task_spec.bpmn_name)
        ready_tasks[0].run()
        self.workflow.do_engine_steps()
        # The inclusive gateway allows us through here, because there is no route for the other thread
        # that doesn't use the same sequence flow
        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRepeatTasksReadyTogetherSaveRestore(self):

        self.save_restore()
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        ready_tasks = self.workflow.get_tasks(TaskState.READY)
        self.assertEqual(2, len(ready_tasks))
        self.assertEqual(
            'Repeated Task', ready_tasks[0].task_spec.bpmn_name)
        ready_tasks[0].run()
        self.workflow.do_engine_steps()
        self.save_restore()
        # The inclusive gateway allows us through here, because there is no route for the other thread
        # that doesn't use the same sequence flow
        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testNoRouteRepeatTaskFirst(self):

        self.save_restore()
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()
        self.save_restore()
        # The inclusive gateway allows this to pass through (since there is a
        # route to it on the same sequence flow)
        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.do_next_named_step('Choice 1', choice='No')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.do_next_named_step('No Task')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testNoRouteNoTaskFirst(self):

        self.save_restore()
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Choice 1', choice='No')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.do_next_named_step('No Task')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testNoRouteNoFirstThenRepeating(self):

        self.save_restore()
        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Choice 1', choice='No')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('No Task')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))
