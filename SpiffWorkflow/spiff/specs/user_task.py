from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

class UserTask(SpiffBpmnTask):
    
    def is_engine_task(self):
        return False
    
    @property
    def spec_type(self):
        return 'User Task'