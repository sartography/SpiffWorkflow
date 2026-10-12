from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.exceptions import WorkflowDataException
from SpiffWorkflow.bpmn.specs.data_spec import TaskDataReference

from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase


class MultiInstanceResetTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.spec, subprocesses = self.load_workflow_spec('multiinstance_reset.bpmn', 'main', validate=False)
        self.workflow = BpmnWorkflow(self.spec, subprocesses)

    def actual_test(self, path, data_input, reset_spec, mi_spec):

        self.workflow.data['data_objects']['input'] = data_input
        start = self.workflow.get_next_task(spec_name='Start')
        start.data['path'] = path
        self.workflow.do_engine_steps()
        task = self.workflow.get_next_task(spec_name=reset_spec, state=TaskState.READY)
        while task is not None:
            task.data['result'] = task.data['item']
            task.run()
            task = self.workflow.get_next_task(spec_name=reset_spec, state=TaskState.READY)

        parent = self.workflow.get_next_task(spec_name=mi_spec, state=TaskState.READY)
        parent.run()

        child = self.workflow.get_next_task(spec_name=reset_spec)
        next_task = self.workflow.get_next_task(spec_name='Gateway_0p9lkom')

        self.workflow.reset_from_task_id(child.id)
        self.assertEqual(child.state, TaskState.READY)
        self.assertEqual(parent.state, TaskState.STARTED)
        self.assertEqual(next_task.state, TaskState.FUTURE)

        child.data['result'] = 4
        child.run()
        parent.run()

    def testParallelListInput(self):
        self.actual_test('parallel', [1, 2, 3], 'task_1 [child]', 'task_1')

