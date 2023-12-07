from .BaseTestCase import BaseTestCase
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow


class DataObjectTest(BaseTestCase):

    def setUp(self):
        self.spec, self.subprocesses = self.load_workflow_spec('data_object.bpmn', 'Process')

    def test_can_get_category_from_data_object(self):
        self.workflow = BpmnWorkflow(self.spec, self.subprocesses)
        category = self.workflow.spec.data_objects['obj_1'].category
        self.assertEqual(category, 'obj_1_category')
        self.save_restore()
