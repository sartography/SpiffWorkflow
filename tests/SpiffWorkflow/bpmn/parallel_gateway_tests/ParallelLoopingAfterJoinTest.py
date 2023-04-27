# -*- coding: utf-8 -*-

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from .BaseParallelTestCase import BaseParallelTestCase

__author__ = 'matth'

class ParallelLoopingAfterJoinTest(BaseParallelTestCase):

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

