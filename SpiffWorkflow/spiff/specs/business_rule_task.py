from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask
from SpiffWorkflow.dmn.specs.BusinessRuleTask import BusinessRuleTask as DefaultBusinessRuleTask

class BusinessRuleTask(DefaultBusinessRuleTask, SpiffBpmnTask):
    pass
