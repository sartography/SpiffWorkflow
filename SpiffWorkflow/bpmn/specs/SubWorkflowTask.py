# -*- coding: utf-8 -*-
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
from ...specs.SubWorkflow import SubWorkflow

from xml.etree import ElementTree as ET

class SubWorkflowTask(SubWorkflow,BpmnSpecMixin):
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

        super(SubWorkflowTask, self).__init__(wf_spec, name, file, **kwargs)        
        pass

    def _create_subworkflow(self, my_task):
        print("in _create_subworkflow")

        print(dir(self))

        print(dir(my_task))

        print(self.name)
        return(self.workflow_spec)
        #x = CamumdaParser.CamundaParser(ET.fromstring(self.xml))
        #return BpmnWorkflow(x.get_spec(self.workflow_spec_name))
        #wf_spec = self.workflow_spec_name
        #print(wf_spec)
        #return BpmnWorkflow(wf_spec)


    def serialize(self, serializer):
        print("serialize subworkflowtask")
        return serializer.serialize_sub_workflow(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_sub_workflow(wf_spec, s_state)
    
