# -*- coding: utf-8 -*-
import json
import os
import sys
import unittest

dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.exceptions import WorkflowTaskExecException
from .BaseTestCase import BaseTestCase

#assertEqual = None

class ServiceTaskDelegate:
    @staticmethod
    def call_connector(name, params):
        if name == 'bamboohr/GetPayRate':
            assertEqual(len(params), 3)
            assertEqual(params['api_key']['value'], 'secret:BAMBOOHR_API_KEY')
            assertEqual(params['employee_id']['value'], '4')
            assertEqual(params['subdomain']['value'], 'ServiceTask')
        elif name == 'weather/CurrentTemp':
            assertEqual(len(params), 1)
            assertEqual(params['zipcode']['value'], '22980')
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
    def available_service_task_external_methods(self):
        return { 'ServiceTaskDelegate': ServiceTaskDelegate }

class ServiceTaskTest(BaseTestCase):

    def setUp(self):
        global assertEqual
        assertEqual = self.assertEqual

        spec, subprocesses = self.load_workflow_spec('service_task.bpmn',
                'service_task_example1')
        self.script_engine = ExampleCustomScriptEngine()
        self.workflow = BpmnWorkflow(spec, subprocesses, script_engine=self.script_engine)

    def testRunThroughHappy(self):
        self.workflow.do_engine_steps()
        self._assert_service_tasks()

    def testRunThroughSaveRestore(self):
        self.save_restore()
        # Engine isn't preserved through save/restore, so we have to reset it.
        self.workflow.script_engine = self.script_engine
        self.workflow.do_engine_steps()
        self.save_restore()
        self._assert_service_tasks()

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


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ServiceTaskTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
