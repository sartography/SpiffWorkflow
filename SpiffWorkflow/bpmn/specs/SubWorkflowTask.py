# -*- coding: utf-8 -*-

# Currently the subworkflow is working correctly, but there is a
# problem with serialize/deserialize. The problem is that the outer
# workflow spec doesn't have a specific spec for the internal
# workflow, so when it tries to pull the internal workflow, it errors
# out when it tries to find the  workflow spec that is associated with
# the task.

# It might be worthwile to remove the classes for the sub
# workflow before serializing, but I'm sure this will lead to problems
# when we do a save/restore in the middle of a subworkflow - so I'm
# left with the prospect that I don't really have the taskspec for the
# items in the subworkflow in the spec that we are save/restoring.

# Specifically, when the subworkflow gets 'expanded' into a new
# workflow, each task has a task spec, but that task spec is in the
# new workflow, and that task spec is NOT in the original workflow
# spec. When it reads in the workflow, it looks for the task_spec in
# the original workflow spec, and it is not there, so it crashes. 

from __future__ import division
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
from .CallActivity import CallActivity
from ..workflow import BpmnWorkflow
from xml.etree import ElementTree as ET

class SubWorkflowTask(CallActivity,BpmnSpecMixin):
    """
    Task Spec for a bpmn:task node. In the base framework, it is assumed that a
    task with an unspecified type is actually a user task
    """

    def __init__(self, wf_spec, name, file=None, lane=None, **kwargs):
        """
        Constructor.

        :param lane: Indicates the name of the lane that this task belongs to
        (optional).
        """

        super(SubWorkflowTask, self).__init__(wf_spec, name, **kwargs)        
        pass

    def create_subworkflow(self, my_task):
        from ...camunda.parser.CamundaParser import CamundaParser
        x = CamundaParser()
        x.add_bpmn_xml(ET.fromstring(self.xml))
        return BpmnWorkflow(x.get_spec(self.workflow_name))



