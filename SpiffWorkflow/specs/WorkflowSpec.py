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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
from SpiffWorkflow.specs import StartTask


class WorkflowSpec(object):
    """
    This class represents the specification of a workflow.
    """

    def __init__(self, name=None, filename=None):
        """
        Constructor.
        """
        self.name = name or ''
        self.description = ''
        self.file = filename
        self.task_specs = dict()
        self.start = StartTask(self)

    def _add_notify(self, task_spec):
        """
        Called by a task spec when it was added into the workflow.
        """
        if task_spec in self.task_specs:
            raise ValueError('duplicate model name: ' + repr(task_spec))
        self.task_specs[task_spec.name] = task_spec
        task_spec.id = len(self.task_specs)

    def get_task_spec_from_name(self, name):
        """
        Returns the task with the given name.

        @type  name: str
        @param name: The name of the task spec.
        @rtype:  TaskSpec
        @return: The task spec with the given name.
        """
        return self.task_specs[name]

    def serialize(self, serializer, **kwargs):
        """
        Serializes the instance using the provided serializer.

        @type  serializer: L{SpiffWorkflow.storage.Serializer}
        @param serializer: The serializer to use.
        @type  kwargs: dict
        @param kwargs: Passed to the serializer.
        @rtype:  object
        @return: The serialized object.
        """
        return serializer.serialize_workflow_spec(self, **kwargs)

    @classmethod
    def deserialize(cls, serializer, s_state, **kwargs):
        """
        Deserializes a WorkflowSpec instance using the provided serializer.

        @type  serializer: L{SpiffWorkflow.storage.Serializer}
        @param serializer: The serializer to use.
        @type  s_state: object
        @param s_state: The serialized workflow specification object.
        @type  kwargs: dict
        @param kwargs: Passed to the serializer.
        @rtype:  WorkflowSpec
        @return: The resulting instance.
        """
        return serializer.deserialize_workflow_spec(s_state, **kwargs)
