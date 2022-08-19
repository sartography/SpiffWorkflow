# -*- coding: utf-8 -*-
import os
import sys
import unittest

dirname = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(dirname, '..', '..', '..'))

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskExecException
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'jbirddog'

class SlackWebhookOperator(object):
    def __init__(self, webhook_token="", message="", channel="", **kwargs):
        super().__init(**kwargs)
        self.channel = channel
        self.message = message
        self.webhook_token = webhook_token

    def execute(self):
        pass

class ServiceTaskTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('service_task.bpmn', 'service_task_example1')
        additions = { 'SlackWebhookOperator': SlackWebhookOperator }
        script_engine = PythonScriptEngine(scriptingAdditions=additions)
        self.workflow = BpmnWorkflow(spec, subprocesses, script_engine=script_engine)

    def testRunThroughHappy(self):
        self.workflow.do_engine_steps()
        # TODO check some indication that it ran

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(ServiceTaskTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
