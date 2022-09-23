from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

class ScriptTask(SpiffBpmnTask):

    def is_engine_task(self):
        return True

    @property
    def spec_type(self):
        return 'Script Task'
