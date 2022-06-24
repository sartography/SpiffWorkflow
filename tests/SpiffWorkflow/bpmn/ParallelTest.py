# -*- coding: utf-8 -*-



from builtins import range
import unittest
import logging
import sys
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class ParallelFromCamunda(BpmnWorkflowTestCase):

    # Should we move this to the Camunda package?  Is this even testing anything Camunda related?

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('Test-Workflows/Parallel.camunda.bpmn20.xml', 'Process_1hb021r')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughParallelTaskFirst(self):

        # 1 first task
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.do_next_named_step('First Task')
        self.save_restore()
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')

        # 3 parallel tasks
        self.assertEqual(3, len(self.workflow.get_tasks(TaskState.READY)))
        self.do_next_named_step('Parallel Task A')
        self.save_restore()
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task B')
        self.save_restore()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task C')
        self.save_restore()
        self.workflow.do_engine_steps()
        self.save_restore()

        # 1 last task
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.READY)))
        self.do_next_named_step('Last Task')
        self.save_restore()
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')

    def testAllParallelDataMakesItIntoGatewayTask(self):
        """It should be true that data collected across parallel tasks
        is all available in the join task."""

        self.do_next_named_step('First Task')
        self.do_next_named_step('Parallel Task A',
                                set_attribs={"taskA": "taskA"})
        self.do_next_named_step('Parallel Task B',
                                set_attribs={"taskB": "taskB"})
        self.do_next_named_step('Parallel Task C',
                                set_attribs={"taskC": "taskC"})
        self.workflow.do_engine_steps()
        self.do_next_named_step('Last Task')
        self.assertEquals("taskA", self.workflow.last_task.data["taskA"])
        self.assertEquals("taskB", self.workflow.last_task.data["taskB"])
        self.assertEquals("taskC", self.workflow.last_task.data["taskC"])


class ParallelJoinLongInclusiveTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('Test-Workflows/Parallel-Join-Long-Inclusive.bpmn20.xml', 'Parallel Join Long Inclusive')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughThread1FirstThenNo(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step(
            'Thread 1 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        for i in range(1, 13):
            self.do_next_named_step('Thread 1 - Task %d' % i)
            self.workflow.do_engine_steps()

        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.do_next_named_step(
            'Thread 2 - Choose', choice='No', with_save_load=True)
        self.workflow.do_engine_steps()
        self.do_next_named_step('Done', with_save_load=True)
        self.workflow.do_engine_steps()
        self.do_next_named_step('Thread 2 - No Task', with_save_load=True)
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testNoFirstThenThread1(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step(
            'Thread 2 - Choose', choice='No', with_save_load=True)
        self.workflow.do_engine_steps()

        self.do_next_named_step(
            'Thread 1 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        for i in range(1, 13):
            self.do_next_named_step('Thread 1 - Task %d' % i)
            self.workflow.do_engine_steps()

        self.do_next_named_step('Done', with_save_load=True)
        self.workflow.do_engine_steps()

        self.do_next_named_step('Thread 2 - No Task', with_save_load=True)
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


class ParallelJoinLongTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('Test-Workflows/Parallel-Join-Long.bpmn20.xml', 'Parallel Join Long')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughAlternating(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step(
            'Thread 1 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        self.do_next_named_step(
            'Thread 2 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()

        for i in range(1, 13):
            self.do_next_named_step(
                'Thread 1 - Task %d' % i, with_save_load=True)
            self.workflow.do_engine_steps()
            self.do_next_named_step(
                'Thread 2 - Task %d' % i, with_save_load=True)
            self.workflow.do_engine_steps()

        self.do_next_named_step('Done', with_save_load=True)
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughThread1First(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step(
            'Thread 1 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        for i in range(1, 13):
            self.do_next_named_step('Thread 1 - Task %d' % i)
            self.workflow.do_engine_steps()

        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.assertEqual(1, len(self.workflow.get_tasks(TaskState.WAITING)))

        self.do_next_named_step(
            'Thread 2 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        for i in range(1, 13):
            self.do_next_named_step(
                'Thread 2 - Task %d' % i, with_save_load=True)
            self.workflow.do_engine_steps()

        self.do_next_named_step('Done', with_save_load=True)
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


class ParallelMultipleSplitsTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('Test-Workflows/Parallel-Multiple-Splits.bpmn20.xml', 'Parallel Multiple Splits')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughAlternating(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Do First')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 1 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 2 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 3 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 1 - Yes Task')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 2 - Yes Task')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 3 - Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


class ParallelOnePathEndsTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('Test-Workflows/Parallel-One-Path-Ends.bpmn20.xml', 'Parallel One Path Ends')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughParallelTaskFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='No')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughChoiceFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Choice 1', choice='No')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughParallelTaskFirstYes(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


class ParallelThenExclusiveTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('Test-Workflows/Parallel-Then-Exclusive.bpmn20.xml', 'Parallel Then Exclusive')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def testRunThroughParallelTaskFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughChoiceFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

    def testRunThroughChoiceThreadCompleteFirst(self):

        self.assertEqual(2, len(self.workflow.get_tasks(TaskState.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


class ParallelThenExclusiveNoInclusiveTest(ParallelThenExclusiveTest):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Then-Exclusive-No-Inclusive.bpmn20.xml', 
            'Parallel Then Exclusive No Inclusive')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

class ParallelThroughSameTaskTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('Test-Workflows/Parallel-Through-Same-Task.bpmn20.xml', 'Parallel Through Same Task')
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

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

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
            'Repeated Task', ready_tasks[0].task_spec.description)
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()
        # The inclusive gateway allows us through here, because there is no route for the other thread
        # that doesn't use the same sequence flow
        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

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
            'Repeated Task', ready_tasks[0].task_spec.description)
        ready_tasks[0].complete()
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

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

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

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

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

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))

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

        self.assertEqual(
            0, len(self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)))


class BaseParallelTest(BpmnWorkflowTestCase):

    def _do_test(self, order, only_one_instance=True, save_restore=False):

        self.workflow.do_engine_steps()
        for s in order:
            choice = None
            if isinstance(s, tuple):
                s, choice = s
            if s.startswith('!'):
                logging.info("Checking that we cannot do '%s'", s[1:])
                self.assertRaises(
                    AssertionError, self.do_next_named_step, s[1:], choice=choice)
            else:
                if choice is not None:
                    logging.info(
                        "Doing step '%s' (with choice='%s')", s, choice)
                else:
                    logging.info("Doing step '%s'", s)
                # logging.debug(self.workflow.get_dump())
                self.do_next_named_step(
                    s, choice=choice, only_one_instance=only_one_instance)
            self.workflow.do_engine_steps()
            if save_restore:
                # logging.debug("Before SaveRestore: \n%s" %
                # self.workflow.get_dump())
                self.save_restore()

        self.workflow.do_engine_steps()
        unfinished = self.workflow.get_tasks(TaskState.READY | TaskState.WAITING)
        if unfinished:
            logging.debug("Unfinished tasks: %s", unfinished)
            logging.debug(self.workflow.get_dump())
        self.assertEqual(0, len(unfinished))


class ParallelMultipleSplitsAndJoinsTest(BaseParallelTest):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Multiple-Splits-And-Joins.bpmn20.xml',
            'Parallel Multiple Splits And Joins')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def test1(self):
        self._do_test(['1', '!Done', '2', '1A', '!Done', '2A', '1B', '2B',
                      '!Done', '1 Done', '!Done', '2 Done', 'Done'], save_restore=True)

    def test2(self):
        self._do_test(
            ['1', '!Done', '1A', '1B', '1 Done', '!Done', '2', '2A', '2B', '2 Done', 'Done'], save_restore=True)

    def test3(self):
        self._do_test(['1', '2', '!Done', '1B', '2B', '!2 Done', '1A',
                      '!Done', '2A', '1 Done', '!Done', '2 Done', 'Done'], save_restore=True)

    def test4(self):
        self._do_test(
            ['1', '1B', '1A', '1 Done', '!Done', '2', '2B', '2A', '2 Done', 'Done'], save_restore=True)


class ParallelLoopingAfterJoinTest(BaseParallelTest):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Looping-After-Join.bpmn20.xml',
            'Parallel Looping After Join')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def test1(self):
        self._do_test(
            ['Go', '1', '2', '2A', '2B', '2 Done', ('Retry?', 'No'), 'Done'], save_restore=True)

    def test2(self):
        self._do_test(
            ['Go', '1', '2', '2A', '2B', '2 Done', ('Retry?', 'Yes'), 'Go',
                     '1', '2', '2A', '2B', '2 Done', ('Retry?', 'No'), 'Done'], save_restore=True)


class ParallelManyThreadsAtSamePointTest(BaseParallelTest):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Many-Threads-At-Same-Point.bpmn20.xml',
            'Parallel Many Threads At Same Point')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def test1(self):
        self._do_test(['1', '2', '3', '4', 'Done', 'Done', 'Done', 'Done'],
                      only_one_instance=False, save_restore=True)

    def test2(self):
        self._do_test(['1', 'Done', '2', 'Done', '3', 'Done',  '4', 'Done'],
                      only_one_instance=False, save_restore=True)

    def test2(self):
        self._do_test(['1', '2', 'Done', '3', '4', 'Done', 'Done', 'Done'],
                      only_one_instance=False, save_restore=True)


class ParallelManyThreadsAtSamePointTestNested(BaseParallelTest):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Many-Threads-At-Same-Point-Nested.bpmn20.xml',
            'Parallel Many Threads At Same Point Nested')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def test_depth_first(self):
        instructions = []
        for split1 in ['SP 1', 'SP 2']:
            for sp in ['A', 'B']:
                for split2 in ['1', '2']:
                    for t in ['A', 'B']:
                        instructions.append(split1 + sp + "|" + split2 + t)
                    instructions.append(split1 + sp + "|" + 'Inner Done')
                    instructions.append("!" + split1 + sp + "|" + 'Inner Done')
                if sp == 'A':
                    instructions.append("!Outer Done")

            instructions.append('Outer Done')
            instructions.append("!Outer Done")

        logging.info('Doing test with instructions: %s', instructions)
        self._do_test(instructions, only_one_instance=False, save_restore=True)

    def test_breadth_first(self):
        instructions = []
        for t in ['A', 'B']:
            for split2 in ['1', '2']:
                for sp in ['A', 'B']:
                    for split1 in ['SP 1', 'SP 2']:
                        instructions.append(split1 + sp + "|" + split2 + t)

        for split1 in ['SP 1', 'SP 2']:
            for sp in ['A', 'B']:
                for split2 in ['1', '2']:
                    instructions += [split1 + sp + "|" + 'Inner Done']

        for split1 in ['SP 1', 'SP 2']:
            instructions += ['Outer Done']

        logging.info('Doing test with instructions: %s', instructions)
        self._do_test(instructions, only_one_instance=False, save_restore=True)


def suite():
    return unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
