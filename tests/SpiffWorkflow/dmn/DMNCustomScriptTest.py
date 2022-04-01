import os
import unittest
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from .BpmnDmnWorkflowTestCase import BpmnDmnWorkflowTestCase


def my_custom_function(txt):
    return str(txt).upper()


class CustomScriptEngine(PythonScriptEngine):

    def __init__(self):
        augment_methods = {'my_custom_function': my_custom_function}
        super().__init__(scriptingAdditions=augment_methods)


class DMNCustomScriptTest(BpmnDmnWorkflowTestCase):

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

    def complete_manual_task(self):
        manual_task = self.workflow.get_tasks_from_spec_name('manual_task')[0]
        self.workflow.complete_task_from_id(manual_task.id)
        self.workflow.do_engine_steps()

    def testDmnHappy(self):
        self.workflow.do_engine_steps()
        self.complete_manual_task()
        self.workflow.do_engine_steps()
        self.assertDictEqual(self.workflow.last_task.data,
                             {'a': 'BILL', 'dmn_result': 'BILL'})

    def testDmnSaveRestore(self):
        self.save_restore()
        self.workflow.script_engine = CustomScriptEngine()
        self.workflow.do_engine_steps()
        self.complete_manual_task()
        self.workflow.do_engine_steps()
        self.assertDictEqual(self.workflow.last_task.data,
                             {'a': 'BILL', 'dmn_result': 'BILL'})


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DMNCustomScriptTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
