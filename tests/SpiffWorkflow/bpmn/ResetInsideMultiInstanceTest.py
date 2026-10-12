import os
import tempfile

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase


class ResetInsideMultiInstanceTest(BpmnWorkflowTestCase):
    """Reset to a task inside a completed iteration of a sequential multi-instance
    subprocess.  The loop reads its input from a data object and writes its output
    to one, and a later task writes the input data object again."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('reset_inside_multiinstance.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def answer(self, value, save_restore=False):
        ready = self.get_ready_user_tasks()
        self.assertEqual(len(ready), 1, "There should only be one task in a ready state.")
        task = ready[0]
        self.assertEqual(task.task_spec.name, 'ask')
        task.data['answer'] = f"{task.data['person']}:{value}"
        task.run()
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()
        return task.id

    def assert_review_ready(self, expected):
        ready = self.get_ready_user_tasks()
        self.assertEqual([t.task_spec.name for t in ready], ['review'])
        self.assertEqual(ready[0].data['collected'], expected)
        self.assertNotIn('answers', ready[0].data)
        collects = [t for t in self.workflow.get_tasks(spec_name='collect')]
        self.assertEqual(len(collects), 1, "The step after the loop should exist once.")

    def testForward(self):
        self.answer('a')
        self.answer('b')
        self.assert_review_ready(['first:a', 'second:b'])

    def testResetToLastIterationAfterLoopCompleted(self):
        self.actual_test(reset_to=1, save_restore=False)

    def testResetToFirstIterationAfterLoopCompleted(self):
        self.actual_test(reset_to=0, save_restore=False)

    def testResetToLastIterationSaveRestore(self):
        self.actual_test(reset_to=1, save_restore=True)

    def testResetToFirstIterationSaveRestore(self):
        self.actual_test(reset_to=0, save_restore=True)

    def testResetTwice(self):
        ids = [self.answer('a'), self.answer('b')]
        self.workflow.reset_from_task_id(ids[1])
        self.workflow.do_engine_steps()
        retry = self.answer('c')
        self.assert_review_ready(['first:a', 'second:c'])
        self.workflow.reset_from_task_id(retry)
        self.workflow.do_engine_steps()
        self.answer('d')
        self.assert_review_ready(['first:a', 'second:d'])

    def testResetWhileLaterIterationIsOpen(self):
        first = self.answer('a')
        self.workflow.reset_from_task_id(first)
        self.workflow.do_engine_steps()
        self.answer('x')
        self.answer('b')
        self.assert_review_ready(['first:x', 'second:b'])

    def actual_test(self, reset_to, save_restore):
        ids = [self.answer('a', save_restore), self.answer('b', save_restore)]
        self.assert_review_ready(['first:a', 'second:b'])

        self.workflow.reset_from_task_id(ids[reset_to])
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()

        if reset_to == 0:
            self.answer('x', save_restore)
            self.answer('y', save_restore)
            self.assert_review_ready(['first:x', 'second:y'])
        else:
            self.answer('y', save_restore)
            self.assert_review_ready(['first:a', 'second:y'])

        self.get_ready_user_tasks()[0].run()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.completed)
        self.assertEqual(self.workflow.data_objects['answers'][-1][-2:], ':y')


class VariantTestCase(BpmnWorkflowTestCase):
    """Runs reset_inside_multiinstance.bpmn with some of its text replaced."""

    replacements = []

    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), 'data', 'reset_inside_multiinstance.bpmn')) as fh:
            xml = fh.read()
        for old, new in self.replacements:
            self.assertIn(old, xml)
            xml = xml.replace(old, new)
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, 'variant.bpmn')
            with open(path, 'w') as fh:
                fh.write(xml)
            spec, subprocesses = self.load_workflow_spec(path, 'main')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def answer(self, task, value, save_restore=False):
        task.data['answer'] = f"{task.data['person']}:{value}"
        task.run()
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()

    def answer_next(self, value, save_restore=False):
        ready = self.get_ready_user_tasks()
        self.assertEqual([t.task_spec.name for t in ready], ['ask'])
        self.answer(ready[0], value, save_restore)
        return ready[0].id

    def collected(self):
        review = self.get_ready_user_tasks()
        self.assertEqual([t.task_spec.name for t in review], ['review'])
        self.assertEqual(len(self.workflow.get_tasks(spec_name='collect')), 1)
        return review[0].data['collected']


class ResetInsideParallelMultiInstanceTest(VariantTestCase):
    """The instances run in parallel: only the reset instance runs again."""

    replacements = [('isSequential="true"', 'isSequential="false"')]

    def actual_test(self, person, save_restore):
        ids = {task.data['person']: task.id for task in self.get_ready_user_tasks()}
        self.assertEqual(sorted(ids), ['first', 'second'])
        for task_id in ids.values():
            self.answer(self.workflow.get_task_from_id(task_id), 'a', save_restore)
        self.assertEqual(sorted(self.collected()), ['first:a', 'second:a'])

        self.workflow.reset_from_task_id(ids[person])
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()
        ready = self.get_ready_user_tasks()
        self.assertEqual([(t.task_spec.name, t.data['person']) for t in ready], [('ask', person)])
        self.answer(ready[0], 'y', save_restore)

        other = 'second' if person == 'first' else 'first'
        self.assertEqual(sorted(self.collected()), sorted([f'{person}:y', f'{other}:a']))

    def testResetToFirstInstance(self):
        self.actual_test('first', save_restore=False)

    def testResetToSecondInstance(self):
        self.actual_test('second', save_restore=False)

    def testResetToFirstInstanceSaveRestore(self):
        self.actual_test('first', save_restore=True)

    def testResetToSecondInstanceSaveRestore(self):
        self.actual_test('second', save_restore=True)


class ResetInsideKeyedMultiInstanceTest(VariantTestCase):
    """The loop runs over a dict, so each instance has to write its output under its own key."""

    replacements = [
        ('people = ["first", "second"]', 'people = {"a": "first", "b": "second"}'),
        ('collected = list(answers)', 'collected = dict(answers)'),
    ]

    def actual_test(self, reset_to, save_restore):
        ids = [self.answer_next('a', save_restore), self.answer_next('b', save_restore)]
        self.assertEqual(self.collected(), {'a': 'first:a', 'b': 'second:b'})
        self.workflow.reset_from_task_id(ids[reset_to])
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()
        if reset_to == 0:
            self.answer_next('x', save_restore)
        self.answer_next('y', save_restore)
        self.assertEqual(self.collected(), {'a': 'first:x' if reset_to == 0 else 'first:a', 'b': 'second:y'})

    def testResetToFirstInstance(self):
        self.actual_test(0, save_restore=False)

    def testResetToLastInstance(self):
        self.actual_test(1, save_restore=False)

    def testResetToFirstInstanceSaveRestore(self):
        self.actual_test(0, save_restore=True)

    def testResetToLastInstanceSaveRestore(self):
        self.actual_test(1, save_restore=True)


class ResetInsideMultiInstanceScriptBeforeFirstTaskTest(VariantTestCase):
    """Each instance starts with a script that appends to a nested list in place.  That must
    not reach the copy of the loop's data the first instance started with, or the
    loop would hand the first instance's entry to the instances after it."""

    replacements = [
        ('people = ["first", "second"]', 'people = ["first", "second"]\nseen = {"names": []}'),
        ('<bpmn:sequenceFlow id="to_ask" sourceRef="person_start" targetRef="ask" />',
         '<bpmn:sequenceFlow id="to_ask" sourceRef="person_start" targetRef="note" />'
         '<bpmn:scriptTask id="note"><bpmn:incoming>to_ask</bpmn:incoming><bpmn:outgoing>to_ask_2</bpmn:outgoing>'
         '<bpmn:script>seen["names"].append(person)</bpmn:script></bpmn:scriptTask>'
         '<bpmn:sequenceFlow id="to_ask_2" sourceRef="note" targetRef="ask" />'),
        ('<bpmn:incoming>to_ask</bpmn:incoming>\n        <bpmn:outgoing>to_person_end</bpmn:outgoing>',
         '<bpmn:incoming>to_ask_2</bpmn:incoming>\n        <bpmn:outgoing>to_person_end</bpmn:outgoing>'),
    ]

    def answer_next(self, value, save_restore=False):
        task = self.get_ready_user_tasks()[0]
        self.assertEqual(task.data["seen"], {"names": [task.data["person"]]})
        return super().answer_next(value, save_restore)

    def testResetToFirstInstance(self):
        first = self.answer_next('a')
        self.answer_next('b')
        self.workflow.reset_from_task_id(first)
        self.workflow.do_engine_steps()
        self.answer_next('x')
        self.answer_next('y')
        self.assertEqual(self.collected(), ['first:x', 'second:y'])


class ResetInsideMultiInstanceCallActivityTest(BpmnWorkflowTestCase):
    """The instances are call activities whose process declares its data inputs, so
    they are handed only those and keep no copy of the loop's data."""

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('reset_inside_multiinstance_call_activity*.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.workflow.do_engine_steps()

    def answer(self, value, save_restore):
        ready = self.get_ready_user_tasks()
        self.assertEqual([t.task_spec.name for t in ready], ['ask'])
        ready[0].data['answer'] = f"{ready[0].data['person']}:{value}"
        ready[0].run()
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()
        return ready[0].id

    def actual_test(self, reset_to, save_restore):
        ids = [self.answer('a', save_restore), self.answer('b', save_restore)]
        self.workflow.reset_from_task_id(ids[reset_to])
        self.workflow.do_engine_steps()
        if save_restore:
            self.save_restore()
        if reset_to == 0:
            self.answer('x', save_restore)
        self.answer('y', save_restore)
        review = self.get_ready_user_tasks()
        self.assertEqual([t.task_spec.name for t in review], ['review'])
        self.assertEqual(review[0].data, {
            'people': ['first', 'second'],
            'kept': 'not passed to the called process',
            'answers': ['first:x' if reset_to == 0 else 'first:a', 'second:y'],
        })

    def testResetToFirstInstance(self):
        self.actual_test(0, save_restore=False)

    def testResetToLastInstance(self):
        self.actual_test(1, save_restore=False)

    def testResetToFirstInstanceSaveRestore(self):
        self.actual_test(0, save_restore=True)

    def testResetToLastInstanceSaveRestore(self):
        self.actual_test(1, save_restore=True)
