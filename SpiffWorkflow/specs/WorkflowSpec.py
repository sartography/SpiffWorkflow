# -*- coding: utf-8 -*-

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

from ..specs import StartTask


class WorkflowSpec(object):

    """
    This class represents the specification of a workflow.
    """

    def __init__(self, name=None, filename=None, nostart=False):
        """
        Constructor.
        """
        self.name = name or ''
        self.description = ''
        self.file = filename
        self.task_specs = dict()
        self.start = None
        if not nostart:
            self.start = StartTask(self)

    def _add_notify(self, task_spec):
        """
        Called by a task spec when it was added into the workflow.
        """
        if task_spec.name in self.task_specs:
            raise KeyError('Duplicate task spec name: ' + task_spec.name)
        self.task_specs[task_spec.name] = task_spec
        task_spec.id = self.name + '_' + str(len(self.task_specs))

    def get_task_spec_from_name(self, name):
        """
        Returns the task with the given name.

        :type  name: str
        :param name: The name of the task spec.
        :rtype:  TaskSpec
        :returns: The task spec with the given name.
        """
        return self.task_specs.get(name)

    def get_task_spec_from_id(self, id):
        """
        Returns the task with the given name.

        :type  name: str
        :param name: The name of the task spec.
        :rtype:  TaskSpec
        :returns: The task spec with the given name.
        """
        ret_spec = None
        for x in self.task_specs:
            if self.task_specs[x].id == id:
                ret_spec = self.task_specs[x]
        return ret_spec


    def validate(self):
        """Checks integrity of workflow and reports any problems with it.

        Detects:
        - loops (tasks that wait on each other in a loop)
        :returns: empty list if valid, a list of errors if not
        """
        results = []
        from ..specs import Join

        def recursive_find_loop(task, history):
            current = history[:]
            current.append(task)
            if isinstance(task, Join):
                if task in history:
                    msg = "Found loop with '%s': %s then '%s' again" % (
                        task.name, '->'.join([p.name for p in history]),
                        task.name)
                    raise Exception(msg)
                for predecessor in task.inputs:
                    recursive_find_loop(predecessor, current)

            for parent in task.inputs:
                recursive_find_loop(parent, current)

        for task_id, task in list(self.task_specs.items()):
            # Check for cyclic waits
            try:
                recursive_find_loop(task, [])
            except Exception as exc:
                results.append(exc.__str__())

            # Check for disconnected tasks
            if not task.inputs and task.name not in ['Start', 'Root']:
                if task.outputs:
                    results.append(f"Task '{task.name}' is disconnected (no inputs)")
                else:
                    results.append(f"Task '{task.name}' is not being used")


        return results

    def serialize(self, serializer, **kwargs):
        """
        Serializes the instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :type  kwargs: dict
        :param kwargs: Passed to the serializer.
        :rtype:  object
        :returns: The serialized object.
        """
        return serializer.serialize_workflow_spec(self, **kwargs)

    @classmethod
    def deserialize(cls, serializer, s_state, **kwargs):
        """
        Deserializes a WorkflowSpec instance using the provided serializer.

        :type  serializer: :class:`SpiffWorkflow.serializer.base.Serializer`
        :param serializer: The serializer to use.
        :type  s_state: object
        :param s_state: The serialized workflow specification object.
        :type  kwargs: dict
        :param kwargs: Passed to the serializer.
        :rtype:  WorkflowSpec
        :returns: The resulting instance.
        """

        return serializer.deserialize_workflow_spec(s_state, **kwargs)

    def get_dump(self, verbose=False):
        done = set()

        def recursive_dump(task_spec, indent):
            if task_spec in done:
                return '[shown earlier] %s (%s:%s)' % (
                    task_spec.name, task_spec.__class__.__name__,
                    hex(id(task_spec))) + '\n'

            done.add(task_spec)
            dump = '%s (%s:%s)' % (
                task_spec.name,
                task_spec.__class__.__name__, hex(id(task_spec))) + '\n'
            if verbose:
                if task_spec.inputs:
                    dump += indent + '-  IN: ' + \
                        ','.join(['%s (%s)' % (t.name, hex(id(t)))
                                  for t in task_spec.inputs]) + '\n'
                if task_spec.outputs:
                    dump += indent + '- OUT: ' + \
                        ','.join(['%s (%s)' % (t.name, hex(id(t)))
                                  for t in task_spec.outputs]) + '\n'
            sub_specs = ([task_spec.spec.start] if hasattr(
                task_spec, 'spec') else []) + task_spec.outputs
            for i, t in enumerate(sub_specs):
                dump += indent + '   --> ' + \
                    recursive_dump(
                        t, indent + ('   |   ' if i + 1 < len(sub_specs) else
                                     '       '))
            return dump

        dump = recursive_dump(self.start, '')

        return dump

    def dump(self):
        print(self.get_dump())
