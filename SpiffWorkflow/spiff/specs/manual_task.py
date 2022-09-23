from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

class ManualTask(SpiffBpmnTask):
    
    def is_engine_task(self):
        return False

    @property
    def spec_type(self):
        return 'Manual Task'