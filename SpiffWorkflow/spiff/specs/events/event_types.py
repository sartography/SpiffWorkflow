from ..spiff_task import SpiffBpmnTask
from SpiffWorkflow.bpmn.specs.events.IntermediateEvent import SendTask, ReceiveTask

class SendTask(SendTask, SpiffBpmnTask):
    pass

class ReceiveTask(ReceiveTask, SpiffBpmnTask):
    pass