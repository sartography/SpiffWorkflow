import json

from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from .BaseTestCase import BaseTestCase


class ServiceTaskDelegate:
    @staticmethod
    def call_connector(name, params, task_data):
        if name == 'bamboohr/GetPayRate':
            assertEqual(len(params), 3)
            assertEqual(params['api_key']['value'], 'secret:BAMBOOHR_API_KEY')
            assertEqual(params['employee_id']['value'], 4)
            assertEqual(params['subdomain']['value'], 'ServiceTask')
        elif name == 'weather/CurrentTemp':
            assertEqual(len(params), 1)
            assertEqual(params['zipcode']['value'], 22980)
        else:
            raise AssertionError('unexpected connector name')

        if name == 'bamboohr/GetPayRate':
            sample_response = {
                "amount": "65000.00",
                "currency": "USD",
                "id": "4",
                "payRate": "65000.00 USD",
            }
        elif name == 'weather/CurrentTemp':
            sample_response = {
                "temp": "72F",
            }

        return json.dumps(sample_response)

class ExampleCustomScriptEngine(PythonScriptEngine):
    def call_service(self, task, operation_name, operation_params):
        return ServiceTaskDelegate.call_connector(operation_name, operation_params, task.data)

class ServiceTaskTest(BaseTestCase):

    def setUp(self):
        global assertEqual
        assertEqual = self.assertEqual

        spec, subprocesses = self.load_workflow_spec('service_task.bpmn','service_task_example1')
        self.script_engine = ExampleCustomScriptEngine()
        self.workflow = BpmnWorkflow(spec, subprocesses, script_engine=self.script_engine)

    def testRunThroughHappy(self):
        self.workflow.do_engine_steps()
        self._assert_service_tasks()

    def testRunSameServiceTaskActivityMultipleTimes(self):
        self.workflow.do_engine_steps()
        service_task_activity = [t for t in self.workflow.get_tasks() if
                                 t.task_spec.name == 'Activity-1inxqgx'][0]

        service_task_activity.task_spec._execute(service_task_activity)
        service_task_activity.task_spec._execute(service_task_activity)
        service_task_activity.task_spec._execute(service_task_activity)

    def testRunThroughSaveRestore(self):
        self.save_restore()
        # Engine isn't preserved through save/restore, so we have to reset it.
        self.workflow.script_engine = self.script_engine
        self.workflow.do_engine_steps()
        self.save_restore()
        self._assert_service_tasks()

    def testServiceTaskRetrySerializationIsSparse(self):
        state = self.serializer.to_dict(self.workflow)
        task_specs = state['spec']['task_specs']

        service_task_without_retry = task_specs['Activity-1inxqgx']
        self.assertNotIn('retries', service_task_without_retry)
        self.assertNotIn('retry_backoff_base', service_task_without_retry)
        self.assertNotIn('retries', service_task_without_retry['extensions']['serviceTaskOperator'])
        self.assertNotIn('retryBackoffBase', service_task_without_retry['extensions']['serviceTaskOperator'])

        service_task_with_retry = task_specs['Activity_12erefa']
        self.assertEqual(service_task_with_retry['retries'], 3)
        self.assertEqual(service_task_with_retry['retry_backoff_base'], 2)
        self.assertEqual(service_task_with_retry['extensions']['serviceTaskOperator']['retries'], 3)
        self.assertEqual(service_task_with_retry['extensions']['serviceTaskOperator']['retryBackoffBase'], 2)

    def testServiceTaskRetrySerializationOmitsBackoffWhenRetriesAreUnset(self):
        service_task = next(
            task for task in self.workflow.get_tasks()
            if task.task_spec.name == 'Activity-1inxqgx'
        )
        service_task.task_spec.retry_backoff_base = 2

        state = self.serializer.to_dict(self.workflow)
        serialized_service_task = state['spec']['task_specs']['Activity-1inxqgx']

        self.assertNotIn('retries', serialized_service_task)
        self.assertNotIn('retry_backoff_base', serialized_service_task)

    def testServiceTaskRetrySerializationOmitsBackoffWhenMissingInXml(self):
        spec, subprocesses = self.load_workflow_spec(
            'service_task_retry_without_backoff.bpmn',
            'service_task_retry_without_backoff',
        )
        workflow = BpmnWorkflow(spec, subprocesses, script_engine=self.script_engine)
        state = self.serializer.to_dict(workflow)
        service_task = state['spec']['task_specs']['Activity_retry_only']

        self.assertEqual(service_task['retries'], 3)
        self.assertNotIn('retry_backoff_base', service_task)
        self.assertEqual(service_task['extensions']['serviceTaskOperator']['retries'], 3)
        self.assertNotIn('retryBackoffBase', service_task['extensions']['serviceTaskOperator'])

        parsed_service_task = [
            task for task in workflow.get_tasks()
            if task.task_spec.name == 'Activity_retry_only'
        ][0]
        self.assertEqual(parsed_service_task.task_spec.retries, 3)
        self.assertIsNone(parsed_service_task.task_spec.retry_backoff_base)

    def _assert_service_tasks(self):
        # service task without result variable name specified, mock
        # bamboohr/GetPayRate response
        result = self.workflow.data['spiff__Activity_1inxqgx_result']
        self.assertEqual(len(result), 4)
        self.assertEqual(result['amount'], '65000.00')
        self.assertEqual(result['currency'], 'USD')
        self.assertEqual(result['id'], '4')
        self.assertEqual(result['payRate'], '65000.00 USD')

        # service task with result variable specified, mock weather response
        result = self.workflow.data['waynesboroWeatherResult']
        self.assertEqual(len(result), 1)
        self.assertEqual(result['temp'], '72F')

        service_task = [t for t in self.workflow.get_tasks() if t.task_spec.name == 'Activity_12erefa'][0]
        self.assertEqual(service_task.task_spec.retries, 3)
        self.assertEqual(service_task.task_spec.retry_backoff_base, 2)
