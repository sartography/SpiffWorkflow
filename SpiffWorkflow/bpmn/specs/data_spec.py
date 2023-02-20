import logging
from copy import deepcopy

from SpiffWorkflow.bpmn.exceptions import WorkflowDataException

data_log = logging.getLogger('spiff.data')


class BpmnDataSpecification:

    def __init__(self, name, description=None):
        """
        :param name: the variable (the BPMN ID)
        :param description: a human readable name (the BPMN name)
        """
        self.name = name
        self.description = description or name
        # In the future, we can add schemas defining the objects here.

    def get(self, my_task, **kwargs):
        raise NotImplementedError

    def set(self, my_task, **kwargs):
        raise NotImplementedError


class BpmnDataStoreSpecification(BpmnDataSpecification):
    def __init__(self, name, description, capacity=None, is_unlimited=None):
        """
        :param name: the name of the task data variable and data store key (the BPMN ID)
        :param description: the task description (the BPMN name)
        :param capacity: the capacity of the data store
        :param is_unlimited: if true capacity is ignored
        """
        self.capacity = capacity or 0
        self.is_unlimited = is_unlimited or True
        # In the future, we can add schemas defining the objects here.
        super().__init__(name, description)


class BpmnIoSpecification:

    def __init__(self, data_inputs, data_outputs):
        self.data_inputs = data_inputs
        self.data_outputs = data_outputs


class DataObject(BpmnDataSpecification):
    """Copy data between process variables and tasks"""

    def get(self, my_task):
        """Copy a value form the workflow data to the task data."""
        if self.name not in my_task.workflow.data:
            message = f"The data object could not be read; '{self.name}' does not exist in the process."
            raise WorkflowDataException(message, my_task, data_input=self)
        my_task.data[self.name] = deepcopy(my_task.workflow.data[self.name])
        data_log.info(f'Read workflow variable {self.name}', extra=my_task.log_info())

    def set(self, my_task):
        """Copy a value from the task data to the workflow data"""
        if self.name not in my_task.data:
            message = f"A data object could not be set; '{self.name}' not exist in the task."
            raise WorkflowDataException(message, my_task, data_output=self)
        my_task.workflow.data[self.name] = deepcopy(my_task.data[self.name])
        del my_task.data[self.name]
        data_log.info(f'Set workflow variable {self.name}', extra=my_task.log_info())


class TaskDataReference(BpmnDataSpecification):
    """A representation of task data that can be used in a BPMN diagram"""
    pass
