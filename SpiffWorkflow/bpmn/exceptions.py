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

from SpiffWorkflow.exceptions import WorkflowTaskException


class WorkflowDataException(WorkflowTaskException):

    def __init__(self, message, task, data_input=None, data_output=None):
        """
        :param task: the task that generated the error
        :param data_input: the spec of the input variable (if a data input)
        :param data_output: the spec of the output variable (if a data output)
        """
        super().__init__(message, task)
        self.data_input = data_input
        self.data_output = data_output
