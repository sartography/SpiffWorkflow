# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from tests.SpiffWorkflow.util import run_workflow
from .TaskSpecTest import TaskSpecTest
from SpiffWorkflow.specs import Transform, Simple


class TransformTest(TaskSpecTest):
    CORRELATE = Transform

    def create_instance(self):
        if 'testtask' in self.wf_spec.task_specs:
            del self.wf_spec.task_specs['testtask']

        return Transform(self.wf_spec,
                         'testtask',
                         description='foo',
                         transforms=[''])

    def testPattern(self):
        """
        Tests that we can create a task that executes an shell command
        and that the workflow can be called to complete such tasks.
        """
        task1 = Transform(self.wf_spec, 'First', transforms=[
            "my_task.set_data(foo=1)"])
        self.wf_spec.start.connect(task1)
        task2 = Transform(self.wf_spec, 'Second', transforms=[
            "my_task.set_data(foo=my_task.data['foo']+1)",
            "my_task.set_data(copy=my_task.data['foo'])"
        ])
        task1.connect(task2)
        task3 = Simple(self.wf_spec, 'Last')
        task2.connect(task3)

        expected = 'Start\n  First\n    Second\n      Last\n'
        workflow = run_workflow(self, self.wf_spec, expected, '')
        first = workflow.get_tasks_from_spec_name('First')[0]
        last = workflow.get_tasks_from_spec_name('Last')[0]
        self.assertEqual(first.data.get('foo'), 1)
        self.assertEqual(last.data.get('foo'), 2)
        self.assertEqual(last.data.get('copy'), 2)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TransformTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
