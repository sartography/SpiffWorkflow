# Copyright (C) 2023 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

import logging
from copy import deepcopy

from SpiffWorkflow.bpmn.exceptions import WorkflowDataException

data_log = logging.getLogger('spiff.data')


class BpmnDataSpecification:

    def __init__(self, bpmn_id, bpmn_name=None):
        """
        :param name: the variable (the BPMN ID)
        :param description: a human readable name (the BPMN name)
        """
        self.bpmn_id = bpmn_id
        self.bpmn_name = bpmn_name
        # In the future, we can add schemas defining the objects here.

    def get(self, my_task, **kwargs):
        raise NotImplementedError

    def set(self, my_task, **kwargs):
        raise NotImplementedError


class BpmnDataStoreSpecification(BpmnDataSpecification):
    def __init__(self, bpmn_id, bpmn_name, capacity=None, is_unlimited=None):
        """
        :param name: the name of the task data variable and data store key (the BPMN ID)
        :param description: the task description (the BPMN name)
        :param capacity: the capacity of the data store
        :param is_unlimited: if true capacity is ignored
        """
        self.capacity = capacity or 0
        self.is_unlimited = is_unlimited or True
        # In the future, we can add schemas defining the objects here.
        super().__init__(bpmn_id, bpmn_name)


class DataObject(BpmnDataSpecification):
    """Copy data between process variables and tasks"""

    def get(self, my_task):
        """Copy a value form the workflow data to the task data."""
        if self.bpmn_id not in my_task.workflow.data:
            message = f"The data object could not be read; '{self.bpmn_id}' does not exist in the process."
            raise WorkflowDataException(message, my_task, data_input=self)
        my_task.data[self.bpmn_id] = deepcopy(my_task.workflow.data[self.bpmn_id])
        data_log.info(f'Read workflow variable {self.bpmn_id}', extra=my_task.log_info())

    def set(self, my_task):
        """Copy a value from the task data to the workflow data"""
        if self.bpmn_id not in my_task.data:
            message = f"A data object could not be set; '{self.bpmn_id}' not exist in the task."
            raise WorkflowDataException(message, my_task, data_output=self)
        my_task.workflow.data[self.bpmn_id] = deepcopy(my_task.data[self.bpmn_id])
        del my_task.data[self.bpmn_id]
        data_log.info(f'Set workflow variable {self.bpmn_id}', extra=my_task.log_info())


class TaskDataReference(BpmnDataSpecification):
    """A representation of task data that can be used in a BPMN diagram"""
    pass
