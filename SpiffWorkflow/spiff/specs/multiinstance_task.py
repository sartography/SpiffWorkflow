from SpiffWorkflow.bpmn.specs.MultiInstanceTask import (
    StandardLoopTask as BpmnStandardLoopTask,
    ParallelMultiInstanceTask as BpmnParallelMITask,
    SequentialMultiInstanceTask as BpmnSequentialMITask,
)
from .spiff_task import SpiffBpmnTask

class StandardLoopTask(BpmnStandardLoopTask, SpiffBpmnTask):
    pass

class ParallelMultiInstanceTask(BpmnParallelMITask, SpiffBpmnTask):
    pass

class SequentialMultiInstanceTask(BpmnSequentialMITask, SpiffBpmnTask):
    pass