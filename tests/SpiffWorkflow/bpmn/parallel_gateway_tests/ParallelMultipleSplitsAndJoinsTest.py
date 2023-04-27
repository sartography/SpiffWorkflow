# -*- coding: utf-8 -*-

from SpiffWorkflow.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from .BaseParallelTestCase import BaseParallelTestCase

__author__ = 'matth'

class ParallelMultipleSplitsAndJoinsTest(BaseParallelTestCase):

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

