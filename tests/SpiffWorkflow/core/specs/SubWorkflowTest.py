import unittest
import os

from lxml import etree

from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from SpiffWorkflow.serializer.prettyxml import XmlSerializer
from SpiffWorkflow.task import TaskState, TaskFilter
from SpiffWorkflow.workflow import Workflow


class TaskSpecTest(unittest.TestCase):

    def testConstructor(self):
        pass  # FIXME

    def testSerialize(self):
        pass  # FIXME

    def testTest(self):
        pass  # FIXME

    def load_workflow_spec(self, folder, f):
        file = os.path.join(
            os.path.dirname(__file__), '..', 'data', folder, f)
        serializer = XmlSerializer()
        with open(file) as fp:
            xml = etree.parse(fp).getroot()
        self.wf_spec = WorkflowSpec.deserialize(
            serializer, xml, filename=file)
        self.workflow = Workflow(self.wf_spec)

    def do_next_unique_task(self, name):
        # This method asserts that there is only one ready task! The specified
        # one - and then completes it
        self.workflow.update_waiting_tasks()
        ready_tasks = self.workflow.get_tasks(task_filter=TaskFilter(state=TaskState.READY))
        self.assertEqual(1, len(ready_tasks))
        task = ready_tasks[0]
        self.assertEqual(name, task.task_spec.name)
        task.run()

    def do_next_named_step(self, name, other_ready_tasks):
        # This method completes a single task from the specified set of ready
        # tasks
        ready_tasks = self.workflow.get_tasks(task_filter=TaskFilter(state=TaskState.READY))
        all_tasks = sorted([name] + other_ready_tasks)
        self.assertEqual(all_tasks, sorted([t.task_spec.name for t in ready_tasks]))
        task = list([t for t in ready_tasks if t.task_spec.name == name])[0]
        task.run()

    def test_block_to_subworkflow(self):
        self.load_workflow_spec('data', 'block_to_subworkflow.xml')
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')

        # Inner.  The subworkflow task will complete automatically after the subwokflow completes
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')

        # Back to outer:
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')

    def test_subworkflow_to_block(self):
        self.load_workflow_spec('data', 'subworkflow_to_block.xml')
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')

        # Inner:
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')
        # Back to outer:
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')

    def test_subworkflow_to_join(self):
        self.load_workflow_spec('control-flow', 'subworkflow_to_join.xml')
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        # The subworkflow task now sets its child tasks to READY and waits
        self.do_next_named_step('second', ['Start'])

        # Inner:
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')
        # Back to outer:
        self.do_next_unique_task('join')
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')

    def test_subworkflow_to_join_refresh_waiting(self):
        self.load_workflow_spec('control-flow', 'subworkflow_to_join.xml')
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')
        self.do_next_named_step('second', ['Start'])

        # Inner:
        self.do_next_unique_task('Start')
        self.do_next_unique_task('first')

        # Update the state of every WAITING task.
        self.workflow.update_waiting_tasks()

        self.do_next_unique_task('last')
        self.do_next_unique_task('End')
        # Back to outer:
        self.do_next_unique_task('join')
        self.do_next_unique_task('last')
        self.do_next_unique_task('End')
