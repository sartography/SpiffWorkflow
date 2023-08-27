from .BpmnWorkflowTestCase import BpmnWorkflowTestCase
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

class DataStoreReferenceTest(BpmnWorkflowTestCase):
    def _do_engine_steps(self, file, processid, save_restore):
        spec, subprocesses = self.load_workflow_spec('data_store.bpmn', 'JustDataStoreRef')
        self.workflow = BpmnWorkflow(spec, subprocesses)
        if save_restore:
            self.save_restore()
        self.workflow.do_engine_steps()

    def _check_last_script_task_data(self):
        last_script_task_data = self.get_first_task_from_spec_name("Activity_1skgyn9").data
        self.assertEqual(len(last_script_task_data), 1)
        self.assertEqual(last_script_task_data["x"], "Sue")

    def testCanInterpretDataStoreReferenceWithInputsAndOutputs(self):
        self._do_engine_steps('data_store.bpmn', 'JustDataStoreRef', False)
        self._check_last_script_task_data()

    def testCanSaveRestoreDataStoreReferenceWithInputsAndOutputs(self):
        self._do_engine_steps('data_store.bpmn', 'JustDataStoreRef', True)
        self._check_last_script_task_data()

    def testSeparateWorkflowInstancesCanShareDataUsingDataStores(self):
        self._do_engine_steps('data_store_write.bpmn', 'JustDataStoreRef', False)
        self._do_engine_steps('data_store_read.bpmn', 'JustDataStoreRef', False)
        self._check_last_script_task_data()

    def testSeparateRestoredWorkflowInstancesCanShareDataUsingDataStores(self):
        self._do_engine_steps('data_store_write.bpmn', 'JustDataStoreRef', True)
        self._do_engine_steps('data_store_read.bpmn', 'JustDataStoreRef', True)
        self._check_last_script_task_data()

