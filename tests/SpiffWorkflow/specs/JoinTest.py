import os
import sys
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from TaskSpecTest import TaskSpecTest
from SpiffWorkflow.specs import Join, Merge, WorkflowSpec, Simple
from SpiffWorkflow import Workflow


class JoinTest(TaskSpecTest):
    CORRELATE = Join

    def create_instance(self):
        return Join(self.wf_spec,
                       'testtask',
                       description='foo')


class MergeTest(TaskSpecTest):
    CORRELATE = Merge

    def create_instance(self):
        return Merge(self.wf_spec,
                       'testtask',
                       description='foo')

    def test_Merge_data_merging(self):
        """Test that Merge task actually merges data"""
        wf_spec = WorkflowSpec()
        first = Simple(wf_spec, 'first')
        second = Simple(wf_spec, 'second')
        third = Simple(wf_spec, 'third')
        bump = Simple(wf_spec, 'bump')
        fourth = Simple(wf_spec, 'fourth')
        merge1 = Merge(wf_spec, 'merge 1')
        simple1 = Simple(wf_spec, 'simple 1')
        merge2 = Merge(wf_spec, 'merge 2')
        simple2 = Simple(wf_spec, 'simple 2')
        unmerged = Simple(wf_spec, 'unmerged')

        wf_spec.start.connect(first)
        wf_spec.start.connect(second)
        wf_spec.start.connect(third)
        wf_spec.start.connect(bump)
        bump.connect(fourth)  # Test join at different depths in tree

        first.connect(merge1)
        second.connect(merge1)
        second.connect(unmerged)

        first.connect(merge2)
        second.connect(merge2)
        third.connect(merge2)
        fourth.connect(merge2)

        merge1.connect(simple1)
        merge2.connect(simple2)

        workflow = Workflow(wf_spec)
        workflow.task_tree.set_attribute(everywhere=1)
        for task in workflow.get_tasks():
            task.set_attribute(**{'name': task.get_name(), task.get_name(): 1})
        workflow.complete_all()
        self.assertTrue(workflow.is_completed())
        found = {}
        for task in workflow.get_tasks():
            if task.task_spec is simple1:
                self.assertIn('first', task.attributes)
                self.assertIn('second', task.attributes)
                self.assertDictEqual(task.attributes, {'Start': 1,
                        'merge 1': 1, 'name': 'Start', 'simple 1': 1,
                        'second': 1, 'first': 1})
                found['simple1'] = task
            if task.task_spec is simple2:
                self.assertIn('first', task.attributes)
                self.assertIn('second', task.attributes)
                self.assertIn('third', task.attributes)
                self.assertIn('fourth', task.attributes)
                self.assertDictEqual(task.attributes, {'merge 2': 1,
                        'simple 2': 1, 'name': 'Start', 'third': 1, 'bump': 1,
                        'Start': 1, 'second': 1, 'first': 1, 'fourth': 1})
                found['simple2'] = task
            if task.task_spec is unmerged:
                self.assertDictEqual(task.attributes, {'Start': 1,
                        'second': 1, 'name': 'Start', 'unmerged': 1})
                found['unmerged'] = task
        self.assertIn('simple1', found)
        self.assertIn('simple2', found)
        self.assertIn('unmerged', found)


def suite():
    tests = unittest.TestLoader().loadTestsFromTestCase(JoinTest)
    tests.addTests(unittest.TestLoader().loadTestsFromTestCase(MergeTest))
    return tests
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
