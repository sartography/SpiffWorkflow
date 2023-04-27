# Copyright (C) 2012 Matthew Hampton, 2023 Sartography
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

from .BpmnSpecMixin import BpmnSpecMixin
from ...specs.Simple import Simple


class ScriptEngineTask(Simple, BpmnSpecMixin):
    """Task Spec for a bpmn:scriptTask node"""

    def _execute(self, task):
        """Please override for specific Implementations, see ScriptTask below for an example"""
        pass

    def _run_hook(self, task):
        return self._execute(task)


class ScriptTask(ScriptEngineTask):

    def __init__(self, wf_spec, name, script, **kwargs):
        """
        Constructor.

        :param script: the script that must be executed by the script engine.
        """
        super(ScriptTask, self).__init__(wf_spec, name, **kwargs)
        self.script = script

    @property
    def spec_type(self):
        return 'Script Task'

    def _execute(self, task):
        return task.workflow.script_engine.execute(task, self.script)
