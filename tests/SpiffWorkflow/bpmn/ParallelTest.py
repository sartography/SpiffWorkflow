# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division, absolute_import
from builtins import range
import unittest
import logging
import sys
from SpiffWorkflow.task import Task
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class ParallelJoinLongTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Join-Long.bpmn20.xml', 'Parallel Join Long')

    def testRunThroughAlternating(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughThread1First(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step(
            'Thread 1 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        for i in range(1, 13):
            self.do_next_named_step('Thread 1 - Task %d' % i)
            self.workflow.do_engine_steps()

        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.assertEqual(1, len(self.workflow.get_tasks(Task.WAITING)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


class ParallelFromCamunda(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('parallel2.bpmn', 'Process_1uzs4e7')

    def testRunThroughParallelTaskFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(1, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Enter SetUp')
        self.save_restore()
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Enter DSP')
        self.save_restore()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Enter Finance')
        self.save_restore()
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertEqual(
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


class ParallelJoinLongInclusiveTest(ParallelJoinLongTest):

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Join-Long-Inclusive.bpmn20.xml', 'Parallel Join Long Inclusive')

    def testRunThroughThread1FirstThenNo(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step(
            'Thread 1 - Choose', choice='Yes', with_save_load=True)
        self.workflow.do_engine_steps()
        for i in range(1, 13):
            self.do_next_named_step('Thread 1 - Task %d' % i)
            self.workflow.do_engine_steps()

        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.assertEqual(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.do_next_named_step(
            'Thread 2 - Choose', choice='No', with_save_load=True)
        self.workflow.do_engine_steps()
        self.do_next_named_step('Done', with_save_load=True)
        self.workflow.do_engine_steps()
        self.do_next_named_step('Thread 2 - No Task', with_save_load=True)
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testNoFirstThenThread1(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


class ParallelMultipleSplitsTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Multiple-Splits.bpmn20.xml', 'Parallel Multiple Splits')

    def testRunThroughAlternating(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


class ParallelThenExlusiveTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Then-Exclusive.bpmn20.xml', 'Parallel Then Exclusive')

    def testRunThroughParallelTaskFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughChoiceFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughChoiceThreadCompleteFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


class ParallelThenExlusiveNoInclusiveTest(ParallelThenExlusiveTest):

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Then-Exclusive-No-Inclusive.bpmn20.xml', 'Parallel Then Exclusive No Inclusive')


class ParallelThroughSameTaskTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Through-Same-Task.bpmn20.xml', 'Parallel Through Same Task')

    def testRunThroughFirstRepeatTaskFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRepeatTasksReadyTogether(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        ready_tasks = self.workflow.get_tasks(Task.READY)
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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRepeatTasksReadyTogetherSaveRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        ready_tasks = self.workflow.get_tasks(Task.READY)
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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testNoRouteRepeatTaskFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testNoRouteNoTaskFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testNoRouteNoFirstThenRepeating(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.save_restore()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


class ParallelOnePathEndsTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-One-Path-Ends.bpmn20.xml', 'Parallel One Path Ends')

    def testRunThroughParallelTaskFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='No')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughChoiceFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Choice 1', choice='No')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEqual(
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughParallelTaskFirstYes(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEqual(2, len(self.workflow.get_tasks(Task.READY)))

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
            0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))


class AbstractParallelTest(BpmnWorkflowTestCase):

    def _do_test(self, order, only_one_instance=True, save_restore=False):
        self.workflow = BpmnWorkflow(self.spec)
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
        unfinished = self.workflow.get_tasks(Task.READY | Task.WAITING)
        if unfinished:
            logging.debug("Unfinished tasks: %s", unfinished)
            logging.debug(self.workflow.get_dump())
        self.assertEqual(0, len(unfinished))


class ParallelMultipleSplitsAndJoinsTest(AbstractParallelTest):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Multiple-Splits-And-Joins.bpmn20.xml', 'Parallel Multiple Splits And Joins')

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


class ParallelLoopingAfterJoinTest(AbstractParallelTest):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Looping-After-Join.bpmn20.xml', 'Parallel Looping After Join')

    def test1(self):
        self._do_test(
            ['Go', '1', '2', '2A', '2B', '2 Done', ('Retry?', 'No'), 'Done'], save_restore=True)

    def test2(self):
        self._do_test(
            ['Go', '1', '2', '2A', '2B', '2 Done', ('Retry?', 'Yes'), 'Go',
                     '1', '2', '2A', '2B', '2 Done', ('Retry?', 'No'), 'Done'], save_restore=True)


class ParallelManyThreadsAtSamePointTest(AbstractParallelTest):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Many-Threads-At-Same-Point.bpmn20.xml', 'Parallel Many Threads At Same Point')

    def test1(self):
        self._do_test(['1', '2', '3', '4', 'Done', 'Done', 'Done', 'Done'],
                      only_one_instance=False, save_restore=True)

    def test2(self):
        self._do_test(['1', 'Done', '2', 'Done', '3', 'Done',  '4', 'Done'],
                      only_one_instance=False, save_restore=True)

    def test2(self):
        self._do_test(['1', '2', 'Done', '3', '4', 'Done', 'Done', 'Done'],
                      only_one_instance=False, save_restore=True)


class ParallelManyThreadsAtSamePointTestNested(AbstractParallelTest):

    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Many-Threads-At-Same-Point-Nested.bpmn20.xml', 'Parallel Many Threads At Same Point Nested')

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
