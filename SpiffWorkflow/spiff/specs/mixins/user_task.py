# Copyright (C) 2025 Sartography
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


from SpiffWorkflow.bpmn.specs.mixins.user_task import UserTask
from SpiffWorkflow.util.deep_merge import DeepMerge

class UserTask(UserTask):
    def __init__(self, wf_spec, bpmn_id, variable=None, **kwargs):
        super().__init__(wf_spec, bpmn_id, **kwargs)
        self.variable = variable

    def add_data_from_form(self, my_task, data):
        if self.variable is not None:
            my_task.set_data(**{self.variable: data})
        else:
            DeepMerge.merge(my_task.data, data)
