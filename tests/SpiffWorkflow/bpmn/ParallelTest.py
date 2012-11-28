import unittest
import logging
import sys
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

class ParallelThenExlusiveTest(BpmnWorkflowTestCase):
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Then-Exclusive.bpmn20.xml', 'Parallel Then Exclusive')

    def testRunThroughParallelTaskFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughChoiceFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughChoiceThreadCompleteFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

class ParallelThroughSameTaskTest(BpmnWorkflowTestCase):
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Through-Same-Task.bpmn20.xml', 'Parallel Through Same Task')

    def testRunThroughFirstRepeatTaskFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRepeatTasksReadyTogether(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEquals(2, len(ready_tasks))
        self.assertEquals('Repeated Task', ready_tasks[0].task_spec.description)
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRepeatTasksReadyTogetherSaveRestore(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        ready_tasks = self.workflow.get_tasks(Task.READY)
        self.assertEquals(2, len(ready_tasks))
        self.assertEquals('Repeated Task', ready_tasks[0].task_spec.description)
        ready_tasks[0].complete()
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Repeated Task')
        self.workflow.do_engine_steps()
        self.save_restore()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

class ParallelOnePathEndsTest(BpmnWorkflowTestCase):
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-One-Path-Ends.bpmn20.xml', 'Parallel One Path Ends')

    def testRunThroughParallelTaskFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='No')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughChoiceFirst(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Choice 1', choice='No')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def testRunThroughParallelTaskFirstYes(self):

        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()

        self.assertEquals(2, len(self.workflow.get_tasks(Task.READY)))

        self.do_next_named_step('Parallel Task')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Choice 1', choice='Yes')
        self.workflow.do_engine_steps()
        self.assertRaises(AssertionError, self.do_next_named_step, 'Done')
        self.do_next_named_step('Yes Task')
        self.workflow.do_engine_steps()

        self.do_next_named_step('Done')
        self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

class ParallelMultipleSplitsAndJoinsTest(BpmnWorkflowTestCase):
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Multiple-Splits-And-Joins.bpmn20.xml', 'Parallel Multiple Splits And Joins')

    def _do_test(self, order):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        for s in order:
            if s.startswith('!'):
                logging.info("Checking that we cannot do '%s'", s[1:])
                self.assertRaises(AssertionError, self.do_next_named_step, s[1:])
            else:
                self.do_next_named_step(s)
            self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def test1(self):
        self._do_test(['1', '!Done', '2', '1A', '!Done', '2A', '1B', '2B', '!Done', '1 Done', '!Done', '2 Done', 'Done'])

    def test2(self):
        self._do_test(['1', '!Done', '1A', '1B', '1 Done', '!Done', '2', '2A', '2B', '2 Done', 'Done'])

    def test3(self):
        self._do_test(['1', '2', '!Done', '1B', '2B', '!2 Done', '1A', '!Done', '2A', '1 Done', '!Done', '2 Done', 'Done'])

    def test4(self):
        self._do_test(['1', '1B', '1A', '1 Done', '!Done', '2', '2B', '2A', '2 Done', 'Done'])


class ParallelLoopingAfterJoinTest(BpmnWorkflowTestCase):
    def setUp(self):
        self.spec = self.load_spec()

    def load_spec(self):
        return self.load_workflow_spec('Test-Workflows/Parallel-Looping-After-Join.bpmn20.xml', 'Parallel Looping After Join')

    def _do_test(self, order):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        for s in order:
            choice = None
            if isinstance(s, tuple):
                s,choice = s
            if s.startswith('!'):
                logging.info("Checking that we cannot do '%s'", s[1:])
                self.assertRaises(AssertionError, self.do_next_named_step, s[1:], choice=choice)
            else:
                if choice is not None:
                    logging.info("Doing step '%s' (with choice='%s')", s, choice)
                else:
                    logging.info("Doing step '%s'", s)
                self.do_next_named_step(s, choice=choice)
            self.workflow.do_engine_steps()

        self.assertEquals(0, len(self.workflow.get_tasks(Task.READY | Task.WAITING)))

    def test1(self):
        self._do_test(['Go', '1', '2', '2A', '2B', '2 Done', ('Retry?', 'No'), 'Done'])

    def test2(self):
        self._do_test(['Go', '1', '2', '2A', '2B', '2 Done', ('Retry?', 'Yes'), 'Go', '1', '2', '2A', '2B', '2 Done', ('Retry?', 'No'), 'Done'])


def suite():
    return unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())