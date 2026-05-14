from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from .BaseTestCase import BaseTestCase


class UserTaskTest(BaseTestCase):

    def setUp(self):
        pass

    def testVariable(self):
        workflow = self.run_workflow('one')
        self.assertIn('order', workflow.data)

    def testNoVariable(self):
        workflow = self.run_workflow('two')
        self.assertIn('size', workflow.data)
        self.assertIn('toppings', workflow.data)

    def run_workflow(self, process_id):
        spec, subprocesses = self.load_workflow_spec('user_task_variable.bpmn', process_id)
        workflow = BpmnWorkflow(spec, subprocesses)
        workflow.do_engine_steps()
        task = workflow.get_next_task(state=TaskState.READY)
        order = {
            'size': 'large',
            'toppings': [
                'sausage',
                'onions',
                'peppers',
            ],
        }
        task.task_spec.add_data_from_form(task, order)
        task.run()
        workflow.do_engine_steps()
        return workflow
