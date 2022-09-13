# -*- coding: utf-8 -*-

# Copyright (C) 2012 Matthew Hampton
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

from .BpmnSpecMixin import BpmnSpecMixin
from ...task import TaskState
from ...specs.Simple import Simple


class ScriptEngineTask(Simple, BpmnSpecMixin):
    """Task Spec for a bpmn:scriptTask node"""

    def _execute(self, task):
        pass

    def _on_ready_hook(self, task):
        super(ScriptEngineTask, self)._on_ready_hook(task)
        task.workflow.script_engine.queue(task)
        task._set_state(TaskState.WAITING)

    def _update_hook(self, task):

        if task.state == TaskState.WAITING:
            if task.workflow.script_engine.is_queued(task):
                if task.workflow._is_busy_with_restore():
                    return
                assert not task.workflow.read_only
                self._execute(task)

            if task.workflow.script_engine.is_complete(task):
                # I don't like updating the task here, but we can't set it to ready
                # or the script will be executed again.
                task.complete()
        else:
            return super()._update_hook(task)

    def serialize(self, serializer):
        return serializer.serialize_script_task(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_script_task(wf_spec, s_state)


class ScriptTask(ScriptEngineTask):

    def __init__(self, wf_spec, name, script, **kwargs):
        """
        Constructor.

        :param script: the script that must be executed by the script engine.
        """
        super(ScriptTask, self).__init__(wf_spec, name, **kwargs)
        self.script = script

    def _execute(self, task):
        task.workflow.script_engine.execute(task, self.script)

