import unittest
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase


def my_custom_function(txt):
    return str(txt).upper()


class CustomScriptEngine(PythonScriptEngine):

    def __init__(self):
        environment = TaskDataEnvironment({'my_custom_function': my_custom_function})
        super().__init__(environment=environment)


class DMNCustomScriptTest(BaseTestCase):

    def setUp(self):

        self.spec, subprocesses = self.load_workflow_spec('CustomScript.bpmn', 'start', 'CustomScript.dmn')
        self.workflow = BpmnWorkflow(self.spec, script_engine=CustomScriptEngine())

    def testConstructor(self):
        pass  # this is accomplished through setup.

    def complete_manual_task(self):
        manual_task = self.workflow.get_tasks_from_spec_name('manual_task')[0]
        self.workflow.run_task_from_id(manual_task.id)
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
