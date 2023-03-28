
import unittest

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from .BaseTestCase import BaseTestCase

class DMNDictTest(BaseTestCase):

    def setUp(self):
        self.spec, subprocesses = self.load_workflow_spec('dmndict.bpmn', 'start', 'dmndict.dmn')
        self.workflow = BpmnWorkflow(self.spec)
        self.expectedResult = {'inputvar': 1,  'pi': {'test': {'me': 'yup it worked'}, 'test2': {'other': 'yes'}}}

    def testDmnHappy(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        x = self.workflow.get_ready_user_tasks()
        self.workflow.run_task_from_id(x[0].id)
        self.workflow.do_engine_steps()
        self.assertDictEqual(self.workflow.last_task.data, self.expectedResult)

    def testDmnSaveRestore(self):
        self.workflow = BpmnWorkflow(self.spec)
        self.workflow.do_engine_steps()
        self.save_restore()
        x = self.workflow.get_ready_user_tasks()
        self.workflow.run_task_from_id(x[0].id)
        self.workflow.do_engine_steps()
        self.save_restore()
        self.assertDictEqual(self.workflow.last_task.data, self.expectedResult)




def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DMNDictTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
