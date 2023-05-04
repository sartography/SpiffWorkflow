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

from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from SpiffWorkflow.bpmn.specs.control import _EndJoin, BpmnStartTask, SimpleBpmnTask


class BpmnProcessSpec(WorkflowSpec):
    """
    This class represents the specification of a BPMN process workflow. This
    specialises the standard Spiff WorkflowSpec class with a few extra methods
    and attributes.
    """

    def __init__(self, name=None, description=None, filename=None, svg=None):
        """
        Constructor.

        :param svg: This provides the SVG representation of the workflow as an
        LXML node. (optional)
        """
        super(BpmnProcessSpec, self).__init__(name=name, filename=filename, nostart=True)
        # Add a root task to ensure all tasks in the workflow are bpmn tasks
        # The serializer ignores this task
        SimpleBpmnTask(self, 'Root')
        self.start = BpmnStartTask(self, 'Start')
        self.end = _EndJoin(self, '%s.EndJoin' % (self.name))
        self.end.connect(SimpleBpmnTask(self, 'End'))
        self.svg = svg
        self.description = description
        self.io_specification = None
        self.data_objects = {}
        self.data_stores = {}
        self.correlation_keys = {}
