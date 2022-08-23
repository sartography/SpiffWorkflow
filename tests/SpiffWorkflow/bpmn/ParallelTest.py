# -*- coding: utf-8 -*-

from builtins import range
import unittest
import logging
import sys
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'

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
