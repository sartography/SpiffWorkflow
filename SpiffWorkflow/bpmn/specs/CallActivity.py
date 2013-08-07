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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.specs.SubWorkflow import SubWorkflow
from SpiffWorkflow.specs.TaskSpec import TaskSpec

class CallActivity(SubWorkflow, BpmnSpecMixin):
    """
    Task Spec for a bpmn:callActivity node.
    """

    def __init__(self, parent, name, wf_spec=None, wf_class=None, **kwargs):
        """
        Constructor.

        :param wf_spec: the BpmnProcessSpec for the sub process.
        :param wf_class: the BpmnWorkflow class to instantiate
        """
        super(CallActivity, self).__init__(parent, name, None, **kwargs)
        self.spec = wf_spec
        self.wf_class = wf_class

    def test(self):
        TaskSpec.test(self)

    def _create_subworkflow(self, my_task):
        return self.get_workflow_class()(self.spec, name=self.name,
            read_only = my_task.workflow.read_only,
            script_engine=my_task.workflow.outer_workflow.script_engine,
            parent = my_task.workflow)

    def get_workflow_class(self):
        """
        Returns the workflow class to instantiate for the sub workflow
        """
        return self.wf_class

    def _on_subworkflow_completed(self, subworkflow, my_task):
        super(CallActivity,self)._on_subworkflow_completed(subworkflow, my_task)
        if isinstance(my_task.parent.task_spec, BpmnSpecMixin):
            my_task.parent.task_spec._child_complete_hook(my_task)
