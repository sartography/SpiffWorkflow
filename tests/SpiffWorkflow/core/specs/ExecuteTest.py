import os
import unittest

from SpiffWorkflow import TaskState
from SpiffWorkflow.specs.Execute import Execute

from .TaskSpecTest import TaskSpecTest
from ..util import run_workflow

class ExecuteTest(TaskSpecTest):

    def create_instance(self):
        if 'testtask' in self.wf_spec.task_specs:
            del self.wf_spec.task_specs['testtask']
        return Execute(self.wf_spec,
                       'testtask',
                       description='foo',
                       args=self.cmd_args)

    def setUp(self):
        script_path = os.path.join(os.path.dirname(__file__), '..', 'ExecuteProcessMock.py')
        self.cmd_args = ["python", script_path]
        TaskSpecTest.setUp(self)

    def testConstructor(self):
        TaskSpecTest.testConstructor(self)
        self.assertEqual(self.spec.args, self.cmd_args)

    def testPattern(self):
        """
        Tests that we can create a task that executes a shell command
        and that the workflow can be called to complete such tasks.
        """
        self.wf_spec.start.connect(self.spec)
        expected = 'Start\n  testtask\n'
        workflow = run_workflow(self, self.wf_spec, expected, '')
        task = self.get_first_task_from_spec_name(workflow, 'testtask')
        self.assertEqual(task.state, TaskState.COMPLETED)
        self.assertIn(b'127.0.0.1', task.results[0])
