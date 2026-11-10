import os
import unittest

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.parser import BpmnParser

# The task that is answered on each path, and whether its instances run in parallel
PATHS = {
    'parallel': ('task_1 [child]', True),
    'sequential': ('task_2 [child]', False),
    'parallel_sp': ('task_3', True),
    'sequential_sp': ('task_4', False),
}


class MultiInstanceResetTest(unittest.TestCase):
    """Reset to an instance of a multiinstance task (a task or a subprocess, sequential or parallel).

    The loop runs over [1, 2, 3]; an instance answers 10 times its item, or 99 after a reset."""

    def start(self, path):
        parser = BpmnParser()
        parser.add_bpmn_file(os.path.join(os.path.dirname(__file__), 'data', 'multiinstance_reset.bpmn'))
        self.workflow = BpmnWorkflow(parser.get_spec('main'), parser.get_subprocess_specs('main'))
        self.workflow.data['data_objects']['input'] = [1, 2, 3]
        self.workflow.get_next_task(spec_name='Start').data['path'] = path
        self.workflow.do_engine_steps()
        self.spec_name = PATHS[path][0]

    def ready(self, item=None):
        tasks = self.workflow.get_tasks(spec_name=self.spec_name, state=TaskState.READY)
        return [t for t in tasks if item is None or t.data['item'] == item]

    def answer(self, item, result=None):
        task = self.ready(item)[0]
        task.data['result'] = item * 10 if result is None else result
        task.run()
        self.workflow.do_engine_steps()
        return task

    def reset(self, task):
        self.workflow.reset_from_task_id(task.id)
        self.workflow.do_engine_steps()

    def finish(self):
        while self.ready():
            self.answer(self.ready()[0].data['item'])
        self.assertTrue(self.workflow.is_completed())
        return self.workflow.data['data_objects']['output']

    def testResetAfterTheLoopFinished(self):
        for path in PATHS:
            for item, expected in (1, [99, 20, 30]), (3, [10, 20, 99]):
                with self.subTest(path=path, item=item):
                    self.start(path)
                    done = {i: self.answer(i) for i in (1, 2, 3)}
                    self.reset(done[item])
                    self.assertEqual([t.data['item'] for t in self.ready()], [item])
                    self.answer(item, 99)
                    self.assertEqual(self.finish(), expected)

    def testResetToAFinishedInstanceWhileTheLoopIsRunning(self):
        for path, (_, parallel) in PATHS.items():
            with self.subTest(path=path):
                self.start(path)
                first = self.answer(1)
                self.reset(first)
                # A sequential loop runs its later instances again after this one
                self.assertEqual([t.data['item'] for t in self.ready()], [1, 2, 3] if parallel else [1])
                self.answer(1, 99)
                self.assertEqual(self.finish(), [99, 20, 30])

    def testResetToAnInstanceThatIsStillRunning(self):
        for path in PATHS:
            with self.subTest(path=path):
                self.start(path)
                self.answer(1)
                self.reset(self.ready(2)[0])
                self.answer(2, 99)
                self.assertEqual(self.finish(), [10, 99, 30])

    def testParallelResultsKeepTheirOrder(self):
        for path in 'parallel', 'parallel_sp':
            with self.subTest(path=path):
                self.start(path)
                done = {i: self.answer(i) for i in (3, 1, 2)}
                self.assertEqual(self.workflow.data['data_objects']['output'], [30, 10, 20])
                # Each result goes back where it was, whichever order the instances are answered in again
                self.reset(done[1])
                self.reset(done[3])
                self.answer(1, 99)
                self.answer(3, 98)
                self.assertEqual(self.finish(), [98, 99, 20])
