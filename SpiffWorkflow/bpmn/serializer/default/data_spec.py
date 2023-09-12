# Copyright (C) 2023 Sartography
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

from SpiffWorkflow.bpmn.specs.data_spec import DataObject, TaskDataReference, BpmnIoSpecification
from ..helpers.registry import BpmnConverter
from ..helpers.spec import BpmnDataSpecificationConverter


class BpmnDataObjectConverter(BpmnDataSpecificationConverter):
    def __init__(self, registry):
        super().__init__(DataObject, registry)


class TaskDataReferenceConverter(BpmnDataSpecificationConverter):
    def __init__(self, registry):
        super().__init__(TaskDataReference, registry)


class IOSpecificationConverter(BpmnConverter):
    def __init__(self, registry):
        super().__init__(BpmnIoSpecification, registry)

    def to_dict(self, spec):
        return {
            'data_inputs': [self.registry.convert(item) for item in spec.data_inputs],
            'data_outputs': [self.registry.convert(item) for item in spec.data_outputs],
        }

    def from_dict(self, dct):
        return BpmnIoSpecification(
            data_inputs=[self.registry.restore(item) for item in dct['data_inputs']],
            data_outputs=[self.registry.restore(item) for item in dct['data_outputs']],
        )
