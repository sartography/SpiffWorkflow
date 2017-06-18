# -*- coding: utf-8 -*-
from __future__ import division
# Copyright (C) 2007 Samuel Abels
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA


class WorkflowException(Exception):

    """
    Base class for all SpiffWorkflow-generated exceptions.
    """

    def __init__(self, sender, error):
        """
        Standard exception class.

        :param sender: the task spec that threw the exception
        :type sender: TaskSpec
        :param error: a human readable error message
        :type error: string
        """
        Exception.__init__(self, '%s: %s' % (sender.name, error))
        self.sender = sender  # Points to the TaskSpec that generated the exception.


class WorkflowTaskExecException(WorkflowException):
    """
    Exception during execution of task "payload". For example:

    * ScriptTask during execution of embedded script,
    * ServiceTask during external service call.
    """

    def __init__(self, task, error):
        """
        Exception initialization.

        :param sender: the task that threw the exception
        :type sender: Task
        :param error: a human readable error message
        :type error: string
        """
        WorkflowException.__init__(self, task.task_spec, error)
        self.task = task


class StorageException(Exception):
    pass
