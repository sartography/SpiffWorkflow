# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
from builtins import object
import sys
import unittest
import re
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from SpiffWorkflow import Task
from SpiffWorkflow.specs import WorkflowSpec, Simple
from SpiffWorkflow.exceptions import WorkflowException


class MockWorkflow(object):
    pass


class TaskTest(unittest.TestCase):

    def setUp(self):
        Task.id_pool = 0
        Task.thread_id_pool = 0

    def testTree(self):
        # Build a tree.
        spec = WorkflowSpec()
        workflow = MockWorkflow()
        task1 = Simple(spec, 'Simple 1')
        task2 = Simple(spec, 'Simple 2')
        task3 = Simple(spec, 'Simple 3')
        task4 = Simple(spec, 'Simple 4')
        task5 = Simple(spec, 'Simple 5')
        task6 = Simple(spec, 'Simple 6')
        task7 = Simple(spec, 'Simple 7')
        task8 = Simple(spec, 'Simple 8')
        task9 = Simple(spec, 'Simple 9')
        root = Task(workflow, task1)
        c1 = root._add_child(task2)
        c11 = c1._add_child(task3)
        c111 = c11._add_child(task4)
        c1111 = Task(workflow, task5, c111)
        c112 = Task(workflow, task6, c11)
        c12 = Task(workflow, task7, c1)
        c2 = Task(workflow, task8, root)
        c3 = Task(workflow, task9, root)
        c3.state = Task.COMPLETED

        # Check whether the tree is built properly.
        expected = """!/0: Task of Simple 1 State: MAYBE Children: 3
  !/0: Task of Simple 2 State: MAYBE Children: 2
    !/0: Task of Simple 3 State: MAYBE Children: 2
      !/0: Task of Simple 4 State: MAYBE Children: 1
        !/0: Task of Simple 5 State: MAYBE Children: 0
      !/0: Task of Simple 6 State: MAYBE Children: 0
    !/0: Task of Simple 7 State: MAYBE Children: 0
  !/0: Task of Simple 8 State: MAYBE Children: 0
  !/0: Task of Simple 9 State: COMPLETED Children: 0"""
        expected = re.compile(expected.replace('!', r'([0-9a-f\-]+)'))
        self.assertTrue(expected.match(root.get_dump()),
                        'Expected:\n' + repr(expected.pattern) + '\n' +
                        'but got:\n' + repr(root.get_dump()))

        # Now remove one line from the expected output for testing the
        # filtered iterator.
        expected2 = ''
        for line in expected.pattern.split('\n'):
            if line.find('Simple 9') >= 0:
                continue
            expected2 += line.lstrip() + '\n'
        expected2 = re.compile(expected2)

        # Run the iterator test.
        result = ''
        for thetask in Task.Iterator(root, Task.MAYBE):
            result += thetask.get_dump(0, False) + '\n'
        self.assertTrue(expected2.match(result),
                        'Expected:\n' + repr(expected2.pattern) + '\n' +
                        'but got:\n' + repr(result))


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TaskTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
