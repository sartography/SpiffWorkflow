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


from SpiffWorkflow.bpmn.specs.bpmn_task_spec import _BpmnCondition
from ..helpers.bpmn_converter import BpmnConverter
from ..helpers.spec import TaskSpecConverter

class IOSpecificationConverter(BpmnConverter):
    """The converter for an IOSpecification"""

    def to_dict(self, spec):
        """Converts an IO spec to a dictionary representation

        Arguments:
            spec (BpmnIOSpecification): the `BpmnIOSpecification` of a `BpmnTaskSpec`

        Returns:
            dict: a dictionary representation of the IO spec
        """
        return {
            'data_inputs': [self.registry.convert(item) for item in spec.data_inputs],
            'data_outputs': [self.registry.convert(item) for item in spec.data_outputs],
        }

    def from_dict(self, dct):
        """Restore a `BpmnIOSpecification` from a dictionary representation

        Arguments:
            dct (dict): the dictionary representation

        Returns:
            `BpmnIOSpecification`: a `BpmnTaskSpec` IO spec
        """
        return self.target_class(
            data_inputs=[self.registry.restore(item) for item in dct['data_inputs']],
            data_outputs=[self.registry.restore(item) for item in dct['data_outputs']],
        )


class BpmnTaskSpecConverter(TaskSpecConverter):
    """The base converter for a `BpmnTaskSpec`

    This converter can be extended for customized task specs with additional attributes (e.g. the
    ones defined in this module, which can serve as examples for anyone who has created a custom
    BPMN task spec.
    """

    def to_dict(self, spec):
        """Create a dictionary representation of the shared `BpmnTaskSpec` attributes

        Arguments:
            spec: the spec to be converter to a dictionary

        Returns:
            dict: a dictionary representation of shared attributes
        """
        return self.get_default_attributes(spec)

    def from_dict(self, dct):
        """Restore a `BpmnTaskSpec` from a dictionary of attributes

        If you have added only custom attributes that can be passed to `__init__`, you won't need
        to extend this.

        Arguments:
            dct (dict): the task spec's dictionary representation

        Returns:
            an instance of the target class
        """
        return self.task_spec_from_dict(dct)


class ScriptTaskConverter(BpmnTaskSpecConverter):
    """The default converter for `ScriptTask`"""

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct['script'] = spec.script
        return dct


class StandardLoopTaskConverter(BpmnTaskSpecConverter):
    """The default converter for `StandardLoopTask`"""

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_standard_loop_attributes(spec))
        return dct


class MultiInstanceTaskConverter(BpmnTaskSpecConverter):
    """The default converter for Parallel and Sequential MultiInstance Tasks"""

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct['task_spec'] = spec.task_spec
        dct['cardinality'] = spec.cardinality
        dct['data_input'] = self.registry.convert(spec.data_input)
        dct['data_output'] = self.registry.convert(spec.data_output)
        dct['input_item'] = self.registry.convert(spec.input_item)
        dct['output_item'] = self.registry.convert(spec.output_item)
        dct['condition'] = spec.condition
        return dct

    def from_dict(self, dct):
        dct['data_input'] = self.registry.restore(dct['data_input'])
        dct['data_output'] = self.registry.restore(dct['data_output'])
        dct['input_item'] = self.registry.restore(dct['input_item'])
        dct['output_item'] = self.registry.restore(dct['output_item'])
        return self.task_spec_from_dict(dct)


class BoundaryEventJoinConverter(BpmnTaskSpecConverter):
    """The default converter for `BoundaryEventJoin`"""

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct.update(self.get_join_attributes(spec))
        return dct

class SubWorkflowConverter(BpmnTaskSpecConverter):
    """The default converter for subworkflows (`SubWOrkflowTask`, `CallActivity`, `TransactionSubprocess`)"""

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct.update(self.get_subworkflow_attributes(spec))
        return dct

    def from_dict(self, dct):
        dct['subworkflow_spec'] = dct.pop('spec')
        return self.task_spec_from_dict(dct)


class ConditionalGatewayConverter(BpmnTaskSpecConverter):
    """A converter class that adds attributes for a `TaskSpec` with conditional outputs"""

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['cond_task_specs'] = [ self.bpmn_condition_to_dict(cond) for cond in spec.cond_task_specs ]
        dct['choice'] = spec.choice
        return dct

    def from_dict(self, dct):
        conditions = dct.pop('cond_task_specs')
        spec = self.task_spec_from_dict(dct)
        spec.cond_task_specs = [ self.bpmn_condition_from_dict(cond) for cond in conditions ]
        return spec

    def bpmn_condition_from_dict(self, dct):
        return (_BpmnCondition(dct['condition']) if dct['condition'] is not None else None, dct['task_spec'])

    def bpmn_condition_to_dict(self, condition):
        expr, task_spec = condition
        return {
            'condition': expr.args[0] if expr is not None else None,
            'task_spec': task_spec
        }


class ExclusiveGatewayConverter(ConditionalGatewayConverter):
    """THe default converterfor `ExclusiveGateway`task specs"""

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['default_task_spec'] = spec.default_task_spec
        return dct

    def from_dict(self, dct):
        default_task_spec = dct.pop('default_task_spec')
        spec = super().from_dict(dct)
        spec.default_task_spec = default_task_spec
        return spec


class ParallelGatewayConverter(BpmnTaskSpecConverter):
    """The default converter for `ParallelGateway` task specs """

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct.update(self.get_join_attributes(spec))
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class EventConverter(BpmnTaskSpecConverter):
    """The default converter for BPMN events"""

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['event_definition'] = self.registry.convert(spec.event_definition)
        return dct

    def from_dict(self, dct):
        dct['event_definition'] = self.registry.restore(dct['event_definition'])
        return self.task_spec_from_dict(dct)


class BoundaryEventConverter(EventConverter):
    """The default converter for `BoundaryEvent` task specs"""

    def to_dict(self, spec):
        dct = super().to_dict(spec)
        dct['cancel_activity'] = spec.cancel_activity
        return dct

