from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase

ASKS = ['g1/k1', 'g1/k2', 'g2/k1', 'g2/k2']
RATES = ['g1', 'g2']


class ResetIntoLoopInstanceTest(BaseTestCase):
    """Reset to a task inside an instance of a loop that has moved on or finished.

    A sequential multi-instance subprocess (with a pre script and a post script
    that removes what the pre script set) contains a standard loop, whose
    instances add to a list.  A multi-instance user task follows.  Whatever
    the reset, answering again must end with the data a straight run ends with.

    The scripts replace values rather than change them in place: tasks share
    nested values with the tasks they inherit from, so a script that appends to
    a list in place also changes the data of earlier tasks, and no reset can be
    right after that.
    """

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('reset_into_loop_instance.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()
        self.ids = {}
        self.save_restore_each_step = False

    def answer(self, value):
        """Answer the one waiting user task; return what it asked about."""
        ready = self.get_ready_user_tasks()
        self.assertEqual(len(ready), 1, "There should only be one task in a ready state.")
        task = ready[0]
        if task.task_spec.name == 'ask':
            asked = self.asked(task)
            task.data['answer'] = value
        else:
            asked = self.asked(task)
            task.data['rating'] = f"{asked}:{value}"
        self.ids[asked] = task.id
        task.run()
        self.workflow.do_engine_steps()
        if self.save_restore_each_step:
            # Each task gets its own copy of its data, as when a workflow is stored between steps
            self.save_restore()
        return asked

    def asked(self, task):
        if task.task_spec.name == 'ask':
            return f"{task.data['group']}/k{3 - task.data['todo']}"
        return task.data['rated']

    def answer_through(self, last, value='a'):
        while self.answer(value) != last:
            pass

    def reset_to(self, asked):
        self.workflow.reset_from_task_id(self.ids[asked])
        self.workflow.do_engine_steps()
        if self.save_restore_each_step:
            self.save_restore()

    def assert_finishes_like_a_straight_run(self, changed):
        """Answer everything that is left with 'a', except `changed`, which gets 'b'."""
        while not self.review_ready():
            self.answer('b' if self.asked(self.get_ready_user_tasks()[0]) == changed else 'a')
        data = self.get_ready_user_tasks()[0].data
        expected_asks = [f"{asked}={'b' if asked == changed else 'a'}" for asked in ASKS]
        self.assertEqual(data, {
            'groups': ['g1', 'g2'],
            'results': [expected_asks[:2], expected_asks[2:]],
            'ratings': [f"{rated}:{'b' if rated == changed else 'a'}" for rated in RATES],
        })
        self.get_ready_user_tasks()[0].run()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.completed)

    def review_ready(self):
        ready = self.get_ready_user_tasks()
        return len(ready) == 1 and ready[0].task_spec.name == 'review'

    def check(self, answered_through, reset_to):
        for self.save_restore_each_step in (False, True):
            with self.subTest(save_restore=self.save_restore_each_step):
                self.setUp_again()
                self.answer_through(answered_through)
                self.reset_to(reset_to)
                waiting = self.get_ready_user_tasks()
                self.assertEqual(len(waiting), 1)
                self.assert_finishes_like_a_straight_run(changed=reset_to)

    def setUp_again(self):
        keep = self.save_restore_each_step
        self.setUp()
        self.save_restore_each_step = keep

    def testStraightRun(self):
        self.assert_finishes_like_a_straight_run(changed=None)

    def testResetToEarlierInstanceOfRunningInnerLoop(self):
        self.check(answered_through='g1/k1', reset_to='g1/k1')

    def testResetIntoFinishedInnerLoopOfRunningInstance(self):
        # the inner loop for g2 has finished; nothing after it has waited yet
        self.check(answered_through='g2/k1', reset_to='g1/k2')

    def testResetIntoEarlierInstanceOfRunningOuterLoop(self):
        self.check(answered_through='g2/k1', reset_to='g1/k1')

    def testResetIntoLastInstanceAfterBothLoopsFinished(self):
        self.check(answered_through='g2/k2', reset_to='g2/k2')

    def testResetIntoFirstInstanceAfterBothLoopsFinished(self):
        self.check(answered_through='g2/k2', reset_to='g1/k1')

    def testResetIntoLoopFromALaterLoop(self):
        self.check(answered_through='g1', reset_to='g2/k1')

    def testResetToInstanceThatIsATask(self):
        self.check(answered_through='g2', reset_to='g1')

    def testResetToLastInstanceThatIsATask(self):
        self.check(answered_through='g2', reset_to='g2')

    def testResetToInstanceThatIsASubprocess(self):
        for self.save_restore_each_step in (False, True):
            with self.subTest(save_restore=self.save_restore_each_step):
                self.setUp_again()
                self.answer_through('g2')
                first_group = self.workflow.get_tasks(spec_name='each_group')[0]
                self.workflow.reset_from_task_id(first_group.id)
                self.workflow.do_engine_steps()
                self.assert_finishes_like_a_straight_run(changed='g1/k1')

    def testResetTwice(self):
        self.answer_through('g2')
        self.reset_to('g1/k2')
        self.answer_through('g2/k1', value='c')
        self.reset_to('g1/k1')
        self.assert_finishes_like_a_straight_run(changed='g1/k1')
