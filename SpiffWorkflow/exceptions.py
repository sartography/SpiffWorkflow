# Copyright (C) 2007 Samuel Abels, 2023 Sartography
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

class SpiffWorkflowException(Exception):
    """
    Base class for all SpiffWorkflow-generated exceptions.
    """
    def __init__(self, msg):
        super().__init__(msg)
        self.notes = []

    def add_note(self, note):
        """add_note is a python 3.11 feature, this can be removed when we
        stop supporting versions prior to 3.11"""
        self.notes.append(note)

    def __str__(self):
        return super().__str__() + ". " + ". ".join(self.notes)


class WorkflowException(SpiffWorkflowException):
    """
    Base class for all SpiffWorkflow-generated exceptions.
    """

    def __init__(self, message, task_spec=None):
        """
        Standard exception class.

        :param task_spec: the task spec that threw the exception
        :type task_spec: TaskSpec
        :param error: a human-readable error message
        :type error: string
        """
        super().__init__(str(message))
        # Points to the TaskSpec that generated the exception.
        self.task_spec = task_spec


class TaskNotFoundException(WorkflowException):
    pass
