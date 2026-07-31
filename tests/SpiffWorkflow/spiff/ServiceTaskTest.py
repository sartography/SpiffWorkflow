import json

from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.spiff.parser import SpiffBpmnParser
from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG
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
        canonical_registry = BpmnWorkflowSerializer.configure(config=DEFAULT_CONFIG)
        self.canonical_serializer = BpmnWorkflowSerializer(registry=canonical_registry)

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
        task_specs = self._get_serialized_task_specs(self.workflow)

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

        serialized_service_task = self._get_serialized_task_specs(self.workflow)['Activity-1inxqgx']

        self.assertNotIn('retries', serialized_service_task)
        self.assertNotIn('retry_backoff_base', serialized_service_task)

    def testServiceTaskRetrySerializationOmitsBackoffWhenMissingInXml(self):
        spec, subprocesses = self.load_workflow_spec(
            'service_task_retry_without_backoff.bpmn',
            'service_task_retry_without_backoff',
        )
        workflow = BpmnWorkflow(spec, subprocesses, script_engine=self.script_engine)
        service_task = self._get_serialized_task_specs(workflow)['Activity_retry_only']

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

    def _get_serialized_task_specs(self, workflow):
        state = self.serializer.to_dict(workflow)
        if 'spec' in state:
            return state['spec']['task_specs']

        restored_workflow = self.serializer.from_dict(state)
        return self.canonical_serializer.to_dict(restored_workflow)['spec']['task_specs']


class EmptyServiceTaskTest(BaseTestCase):

    BPMN = '''<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:spiffworkflow="http://spiffworkflow.org/bpmn/schema/1.0/core" id="Definitions_1" targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="empty_service_task" name="EmptyServiceTask" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1"><bpmn:outgoing>Flow_1</bpmn:outgoing></bpmn:startEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="Activity_1" />
    <bpmn:serviceTask id="Activity_1" name="EmptyServiceTask">
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_2</bpmn:outgoing>
    </bpmn:serviceTask>
    <bpmn:sequenceFlow id="Flow_2" sourceRef="Activity_1" targetRef="Event_1" />
    <bpmn:endEvent id="Event_1"><bpmn:incoming>Flow_2</bpmn:incoming></bpmn:endEvent>
  </bpmn:process>
</bpmn:definitions>
'''

    def test_service_task_without_operator_raises_useful_error(self):
        parser = SpiffBpmnParser()
        parser.add_bpmn_str(self.BPMN)
        with self.assertRaises(ValidationException) as ctx:
            parser.get_spec('empty_service_task')
        self.assertIn('A Service Task must have an operator', str(ctx.exception))
