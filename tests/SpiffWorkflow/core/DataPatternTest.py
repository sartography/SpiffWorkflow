# -*- coding: utf-8 -*-
from unittest import TestCase
from .pattern_base import WorkflowPatternTestCase


class TaskDataTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('data/task_data')

class BlockDataTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('data/block_data')

class TaskToTaskTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('data/task_to_task')

class BlockToSubworkflowTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('data/block_to_subworkflow')

class SubworkflowTOBlockTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('data/subworkflow_to_block')