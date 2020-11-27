import os
import unittest

from SpiffWorkflow import Task

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

class DMNDictTest(BpmnWorkflowTestCase):
    PARSER_CLASS = BpmnDmnParser

    def setUp(self):
        parser = BpmnDmnParser()
        bpmn = os.path.join(os.path.dirname(__file__), 'data', 'BpmnDmn',
                            'dmndict.bpmn')
        dmn = os.path.join(os.path.dirname(__file__), 'data', 'BpmnDmn',
                            'dmndict.dmn')
        parser.add_bpmn_file(bpmn)
        parser.add_dmn_file(dmn)
        self.expectedResult = {'inputvar': 1,  'pi': {'test': {'me': 'yup it worked'}, 'test2': {'other': 'yes'}}}
        self.spec = parser.get_spec('start')
        self.workflow = BpmnWorkflow(self.spec)

    def testConstructor(self):
        pass  # this is accomplished through setup.

    def testDmnHappy(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.assertDictEqual(self.workflow.last_task.data, self.expectedResult)

    def testDmnSaveRestore(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertDictEqual(self.workflow.last_task.data, self.expectedResult)




def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DMNDictTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
