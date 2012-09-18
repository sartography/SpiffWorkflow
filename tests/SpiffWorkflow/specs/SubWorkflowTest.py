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

    def load_workflow_spec(self, f):
        file = os.path.join(os.path.dirname(__file__), '..', 'data', 'spiff', 'data', f)
        serializer    = XmlSerializer()
        xml           = open(file).read()
        self.wf_spec  = WorkflowSpec.deserialize(serializer, xml, filename = file)
        self.workflow = Workflow(self.wf_spec)

    def do_next_unique_step(self, name):
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEquals(1, len(ready_tasks))
        task = ready_tasks[0]
        self.assertEquals(name, task.task_spec.name)
        task.complete()


    def test_block_to_subworkflow(self):
        self.load_workflow_spec('block_to_subworkflow.xml')
        self.do_next_unique_step('Start')
        self.do_next_unique_step('first')
        self.do_next_unique_step('sub_workflow_1')
        #Inner:
        self.do_next_unique_step('Start')
        self.do_next_unique_step('first')
        self.do_next_unique_step('last')
        self.do_next_unique_step('End')
        #Back to outer:
        self.do_next_unique_step('last')
        self.do_next_unique_step('End')

    def test_subworkflow_to_block(self):
        self.load_workflow_spec('subworkflow_to_block.xml')
        self.do_next_unique_step('Start')
        self.do_next_unique_step('first')
        self.do_next_unique_step('sub_workflow_1')
        #Inner:
        self.do_next_unique_step('Start')
        self.do_next_unique_step('first')
        self.do_next_unique_step('last')
        self.do_next_unique_step('End')
        #Back to outer:
        self.do_next_unique_step('last')
        self.do_next_unique_step('End')




def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TaskSpecTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
