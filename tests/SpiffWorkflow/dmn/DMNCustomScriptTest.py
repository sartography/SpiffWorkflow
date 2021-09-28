import os
import unittest
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase


def my_custom_function(txt):
    return str(txt).upper()


class CustomScriptEngine(PythonScriptEngine):
    def execute(self, task, script, data, **kwargs):
        augment_methods = {'my_custom_function': my_custom_function}
        super().execute(task, script, data, external_methods=augment_methods)

    def eval(self, exp, data):
        return super()._eval(exp, {}, **data)


class DMNCustomScriptTest(BpmnWorkflowTestCase):
    PARSER_CLASS = BpmnDmnParser

    def setUp(self):
        parser = BpmnDmnParser()
        bpmn = os.path.join(os.path.dirname(__file__), 'data', 'BpmnDmn',
                            'CustomScript.bpmn')
        dmn = os.path.join(os.path.dirname(__file__), 'data', 'BpmnDmn',
                           'CustomScript.dmn')
        parser.add_bpmn_file(bpmn)
        parser.add_dmn_file(dmn)
        self.spec = parser.get_spec('start')
        self.workflow = BpmnWorkflow(self.spec,
                                     script_engine=CustomScriptEngine())

    def testConstructor(self):
        pass  # this is accomplished through setup.

    def testDmnHappy(self):
        self.workflow.do_engine_steps()
        self.assertDictEqual(self.workflow.last_task.data,
                             {'a': 'BILL', 'dmn_result': 'BILL'})

    def testDmnSaveRestore(self):
        self.workflow = BpmnWorkflow(self.spec,
                                     script_engine=CustomScriptEngine())
        self.save_restore()
        self.workflow.do_engine_steps()
        self.assertDictEqual(self.workflow.last_task.data,
                             {'a': 'BILL', 'dmn_result': 'BILL'})


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DMNCustomScriptTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
