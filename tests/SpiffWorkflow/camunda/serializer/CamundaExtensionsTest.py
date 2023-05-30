import unittest

from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

from tests.SpiffWorkflow.camunda.BaseTestCase import BaseTestCase


class CamundaExtensionsTest(BaseTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('random_fact.bpmn', 'random_fact')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testExtensionsAreSerialized(self):
        self.assertMyExtension()
        self.save_restore()
        self.assertMyExtension()

    def assertMyExtension(self):
        """Assure that we have a very specific extension on specific task."""
        task = self.workflow.spec.get_task_spec_from_name("Task_User_Select_Type")
        self.assertIsNotNone(task)
        self.assertTrue(hasattr(task, 'extensions'))
        self.assertTrue("my_extension" in task.extensions)
        self.assertEqual(task.extensions["my_extension"], 'my very own extension')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(CamundaExtensionsTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
