# -*- coding: utf-8 -*-

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from .BaseParallelTestCase import BaseParallelTestCase

__author__ = 'matth'

class ParallelManyThreadsAtSamePointTest(BaseParallelTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec(
            'Test-Workflows/Parallel-Many-Threads-At-Same-Point.bpmn20.xml',
            'sid-6d1186e0-fc1f-43d5-bdb4-c49df043944d')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def test1(self):
        self._do_test(['1', '2', '3', '4', 'Done', 'Done', 'Done', 'Done'],
                      only_one_instance=False, save_restore=True)

    def test2(self):
        self._do_test(['1', 'Done', '2', 'Done', '3', 'Done',  '4', 'Done'],
                      only_one_instance=False, save_restore=True)

    def test3(self):
        self._do_test(['1', '2', 'Done', '3', '4', 'Done', 'Done', 'Done'],
                      only_one_instance=False, save_restore=True)

