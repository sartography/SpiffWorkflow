from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask
from SpiffWorkflow.bpmn.specs.ScriptTask import ScriptTask as BpmnScriptTask


class ScriptTask(BpmnScriptTask, SpiffBpmnTask):
    pass
