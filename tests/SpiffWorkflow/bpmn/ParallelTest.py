import unittest
import datetime
import time
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnWorkflow
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'matth'


class ParallelJoinLongTest(BpmnWorkflowTestCase):
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Join-Long.bpmn20.xml', 'Parallel Join Long')

    def testRunThroughAlternating(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Thread 1 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Thread 2 - Choose', choice='Yes')
        self.workflow.do_engine_steps()

        for i in range(1,13):
            self.do_next_named_step('Thread 1 - Task %d' % i)
            self.workflow.do_engine_steps()
            self.do_next_named_step('Thread 2 - Task %d' % i)
            self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughThread1First(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Thread 1 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        for i in range(1,13):
            self.do_next_named_step('Thread 1 - Task %d' % i)
            self.workflow.do_engine_steps()

        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.assertEquals(1, len(self.workflow.get_tasks(Task.WAITING)))

        self.do_next_named_step('Thread 2 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        for i in range(1,13):
            self.do_next_named_step('Thread 2 - Task %d' % i)
            self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

class ParallelMultipleSplitsTest(BpmnWorkflowTestCase):
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Multiple-Splits.bpmn20.xml', 'Parallel Multiple Splits')

    def testRunThroughAlternating(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Do First')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 1 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 2 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 3 - Choose', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 1 - Yes Task')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 2 - Yes Task')
        self.workflow.do_engine_steps()
        self.do_next_named_step('SP 3 - Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ParallelJoinLongTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())