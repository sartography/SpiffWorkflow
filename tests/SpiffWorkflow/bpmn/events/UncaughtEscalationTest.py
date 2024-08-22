import unittest

from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow

from ..BpmnWorkflowTestCase import BpmnWorkflowTestCase

class UncaughtEscalationTest(BpmnWorkflowTestCase):

    def test_uncaught_escalation(self):
        spec, subprocess_specs = self.load_workflow_spec('uncaught_escalation.bpmn', 'top_level')
        workflow = BpmnWorkflow(spec, subprocess_specs)
        workflow.do_engine_steps()
        self.assertTrue(workflow.completed)
        event = workflow.get_events()[0]
        self.assertEqual(event.event_definition.code, 'escalation-1')

