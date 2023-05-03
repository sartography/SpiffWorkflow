from SpiffWorkflow.bpmn.specs.mixins.user_task import UserTask as UserTaskMixin
from SpiffWorkflow.bpmn.specs.mixins.manual_task import ManualTask as ManualTaskMixin
from SpiffWorkflow.bpmn.specs.mixins.none_task import NoneTask as NoneTaskMixin
from SpiffWorkflow.bpmn.specs.mixins.script_task import ScriptTask as ScriptTaskMixin

from SpiffWorkflow.bpmn.specs.mixins.events.intermediate_event import SendTask, ReceiveTask

from SpiffWorkflow.bpmn.specs.mixins.subworkfow_task import(
    SubWorkflowTask as SubWorkflowTaskMixin,
    CallActivity as CallActivityMixin,
    TransactionSubprocess as TransactionSubprocessMixin,
)
from SpiffWorkflow.bpmn.specs.mixins.multiinstance_task import (
    StandardLoopTask as BpmnStandardLoopTask,
    ParallelMultiInstanceTask as BpmnParallelMITask,
    SequentialMultiInstanceTask as BpmnSequentialMITask,
)

from SpiffWorkflow.dmn.specs.business_rule_task_mixin import BusinessRuleTaskMixin as DefaultBusinessRuleTask

from .mixins.service_task import ServiceTask as ServiceTaskMixin

from .spiff_task import SpiffBpmnTask


class UserTask(UserTaskMixin, SpiffBpmnTask):
    pass

class ManualTask(ManualTaskMixin, SpiffBpmnTask):
    pass

class NoneTask(NoneTaskMixin, SpiffBpmnTask):
    pass

class ScriptTask(ScriptTaskMixin, SpiffBpmnTask):
    pass

class SendTask(SendTask, SpiffBpmnTask):
    pass

class ReceiveTask(ReceiveTask, SpiffBpmnTask):
    pass

class StandardLoopTask(BpmnStandardLoopTask, SpiffBpmnTask):
    pass

class ParallelMultiInstanceTask(BpmnParallelMITask, SpiffBpmnTask):
    pass

class SequentialMultiInstanceTask(BpmnSequentialMITask, SpiffBpmnTask):
    pass

class BusinessRuleTask(DefaultBusinessRuleTask, SpiffBpmnTask):
    pass

class SubWorkflowTask(SubWorkflowTaskMixin, SpiffBpmnTask):
    pass

class CallActivity(CallActivityMixin, SpiffBpmnTask):
    pass

class TransactionSubprocess(TransactionSubprocessMixin, SpiffBpmnTask):
    pass

class ServiceTask(ServiceTaskMixin, SpiffBpmnTask):
    pass