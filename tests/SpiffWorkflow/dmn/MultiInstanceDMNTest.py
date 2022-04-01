import os
import unittest

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from .BpmnDmnWorkflowTestCase import BpmnDmnWorkflowTestCase

class MultiInstanceDMNTest(BpmnDmnWorkflowTestCase):

    def setUp(self):
        parser = BpmnDmnParser()
        bpmn = os.path.join(os.path.dirname(__file__), 'data', 'BpmnDmn',
                            'DMNMultiInstance.bpmn')
        dmn = os.path.join(os.path.dirname(__file__), 'data', 'BpmnDmn',
                            'test_integer_decision_multi.dmn')
        parser.add_bpmn_file(bpmn)
        parser.add_dmn_file(dmn)
        self.spec = parser.get_spec('Process_1')
        self.workflow = BpmnWorkflow(self.spec)

    def testConstructor(self):
        pass  # this is accomplished through setup.

    def testDmnHappy(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.workflow.complete_next()
        self.workflow.do_engine_steps()
        self.workflow.complete_next()
        self.workflow.do_engine_steps()
        self.assertEqual(self.workflow.data['stuff']['E']['y'], 'D')


    def testDmnSaveRestore(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.save_restore()
        self.workflow.do_engine_steps()
        self.workflow.complete_next()
        self.save_restore()
        self.workflow.do_engine_steps()
        self.workflow.complete_next()
        self.save_restore()
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertEqual(self.workflow.data['stuff']['E']['y'], 'D')



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MultiInstanceDMNTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
