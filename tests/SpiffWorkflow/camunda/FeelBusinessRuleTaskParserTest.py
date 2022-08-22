import unittest

from SpiffWorkflow import TaskState

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase

class FeelBusinessRuleTaskParserTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocesses = self.load_workflow_spec(
            'ExclusiveGatewayIfElseAndDecision.bpmn', 'Process_1',  'test_integer_decision_feel.dmn')
        self.workflow = BpmnWorkflow(self.spec)

    def testConstructor(self):
        pass  # this is accomplished through setup.

    def testDmnHappy(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.get_tasks(TaskState.READY)[0].set_data(x=3)
        self.workflow.do_engine_steps()
        self.assertDictEqual(self.workflow.data, {'x': 3, 'y': 'A'})
        self.assertDictEqual(self.workflow.last_task.data, {'x': 3, 'y': 'A'})

    def testDmnSaveRestore(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.get_tasks(TaskState.READY)[0].set_data(x=3)
        self.save_restore()
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertDictEqual(self.workflow.data, {'x': 3, 'y': 'A'})
        self.assertDictEqual(self.workflow.last_task.data, {'x': 3, 'y': 'A'})




def suite():
    return unittest.TestLoader().loadTestsFromTestCase(FeelBusinessRuleTaskParserTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
