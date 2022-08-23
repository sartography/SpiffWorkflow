# -*- coding: utf-8 -*-

import unittest
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BaseParallelTestCase import BaseParallelTestCase

__author__ = 'matth'

class ParallelManyThreadsAtSamePointTest(BaseParallelTestCase):

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


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ParallelManyThreadsAtSamePointTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
