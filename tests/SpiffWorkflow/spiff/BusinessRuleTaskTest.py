from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase

class BusinessRuleTaskTest(BaseTestCase):

    def testBusinessRule(self):
        spec, subprocesses = self.load_workflow_spec('business_rule_task.bpmn', 'Process_bd2e724', 'business_rules.dmn')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        self.save_restore()
        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.is_completed())