import sys
import unittest
import re
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from SpiffWorkflow.specs import WorkflowSpec, Simple, Join
from SpiffWorkflow.specs.SubWorkflow import SubWorkflow
from SpiffWorkflow.storage import XmlSerializer
from SpiffWorkflow.Task import Task
from SpiffWorkflow.Workflow import Workflow

class TaskSpecTest(unittest.TestCase):
    CORRELATE = SubWorkflow

    def testConstructor(self):
        pass #FIXME

    def testSerialize(self):
        pass #FIXME

    def testTest(self):
        pass #FIXME

    def load_workflow_spec(self, folder, f):
        file = os.path.join(os.path.dirname(__file__), '..', 'data', 'spiff', folder, f)
        serializer    = XmlSerializer()
        xml           = open(file).read()
        self.wf_spec  = WorkflowSpec.deserialize(serializer, xml, filename = file)
        self.workflow = Workflow(self.wf_spec)

    def do_next_unique_task(self, name):
        #This method asserts that there is only one ready task! The specified one - and then completes it
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEquals(1, len(ready_tasks))
        task = ready_tasks[0]
        self.assertEquals(name, task.task_spec.name)
        task.complete()

    def do_next_named_step(self, name, other_ready_tasks):
        #This method completes a single task from the specified set of ready tasks
        ready_tasks = self.workflow.get_tasks(Task.READY)
        all_tasks = sorted([name] + other_ready_tasks)
        self.assertEquals(all_tasks, sorted([t.task_spec.name for t in ready_tasks]))
        task = filter(lambda t: t.task_spec.name==name, ready_tasks)[0]
        task.complete()


    def test_block_to_subworkflow(self):
        self.load_workflow_spec('data', 'block_to_subworkflow.xml')
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        self.do_next_unique_task('sub_workflow_1')
        #Inner:
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')
        #Back to outer:
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')

    def test_subworkflow_to_block(self):
        self.load_workflow_spec('data', 'subworkflow_to_block.xml')
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        self.do_next_unique_task('sub_workflow_1')
        #Inner:
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')
        #Back to outer:
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')

    def test_subworkflow_to_join(self):
        self.load_workflow_spec('control-flow', 'subworkflow_to_join.xml')
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        self.do_next_named_step('second', ['sub_workflow_1'])
        self.do_next_unique_task('sub_workflow_1')
        #Inner:
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')
        #Back to outer:
        self.do_next_unique_task('join')
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')

    def test_subworkflow_to_join_refresh_waiting(self):
        self.load_workflow_spec('control-flow', 'subworkflow_to_join.xml')
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        self.do_next_named_step('second', ['sub_workflow_1'])
        self.do_next_unique_task('sub_workflow_1')
        #Inner:
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')

        #Now refresh waiting tasks:
        # Update the state of every WAITING task.
        for thetask in self.workflow._get_waiting_tasks():
            thetask.task_spec._update_state(thetask)

        self.do_next_unique_task('last')
        self.do_next_unique_task('End')
        #Back to outer:
        self.do_next_unique_task('join')
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TaskSpecTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
