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

from .ValidationException import ValidationException
from .TaskParser import TaskParser
from .util import one


class GatewayParser(TaskParser):
    def handles_multiple_outgoing(self):
        return True


class ConditionalGatewayParser(GatewayParser):
    """
    Parses an Exclusive Gateway, setting up the outgoing conditions
    appropriately.
    """
    def connect_outgoing(self, outgoing_task, sequence_flow_node, is_default):
        if is_default:
            super().connect_outgoing(outgoing_task, sequence_flow_node, is_default)
        else:
            cond = self.parse_condition(sequence_flow_node)
            if cond is None:
                raise ValidationException(
                    'Non-default exclusive outgoing sequence flow without condition',
                    sequence_flow_node,
                    self.filename)
            self.task.connect_outgoing_if(cond, outgoing_task)


class SubprocessParser:

    # Not really a fan of this, but I need a way of calling these methods from a task
    # parser that extends the base parser to override extension parsing.  I can't inherit
    # from my extended task parser AND the original subworkflow parsers because they
    # both inherit from the same base.

    @staticmethod
    def get_subprocess_spec(task_parser):

        workflow_start_event = task_parser.xpath('./bpmn:startEvent')
        workflow_end_event = task_parser.xpath('./bpmn:endEvent')
        if len(workflow_start_event) != 1:
            raise ValidationException(
                f'Exactly one start event is required in a SubWorkflow Task; found {len(workflow_start_event)}.',
                node=task_parser.node,
                file_name=task_parser.filename)
        if len(workflow_end_event) == 0:
            raise ValidationException('A SubWorkflow Must contain an End event',
                node=task_parser.node,
                file_name=task_parser.filename)

        task_parser.process_parser.parser.create_parser(
            task_parser.node,
            filename=task_parser.filename,
            lane=task_parser.lane
        )
        spec_id = task_parser.node.get('id')
        # This parser makes me want to cry
        spec_parser = task_parser.process_parser.parser.process_parsers[spec_id]
        spec_parser.inherited_data_objects.update(task_parser.process_parser.spec.data_objects)
        return spec_id

    @staticmethod
    def get_call_activity_spec(task_parser):

        called_element = task_parser.node.get('calledElement', None)
        if not called_element:
            raise ValidationException(
                'No "calledElement" attribute for Call Activity.',
                node=task_parser.node,
                file_name=task_parser.filename)
        return called_element


class SubWorkflowParser(TaskParser):

    def create_task(self):
        subworkflow_spec = SubprocessParser.get_subprocess_spec(self)
        return self.spec_class(self.spec, self.bpmn_id, subworkflow_spec=subworkflow_spec, **self.bpmn_attributes)


class CallActivityParser(TaskParser):
    """Parses a CallActivity node."""

    def create_task(self):
        subworkflow_spec = SubprocessParser.get_call_activity_spec(self)
        return self.spec_class(self.spec, self.bpmn_id, subworkflow_spec=subworkflow_spec, **self.bpmn_attributes)


class ScriptTaskParser(TaskParser):
    """Parses a script task"""

    def create_task(self):
        return self.spec_class(self.spec, self.bpmn_id, script=self.get_script(), **self.bpmn_attributes)

    def get_script(self):
        """
        Gets the script content from the node. A subclass can override this
        method, if the script needs to be pre-parsed. The result of this call
        will be passed to the Script Engine for execution.
        """
        try:
            return one(self.xpath('.//bpmn:script')).text
        except AssertionError as ae:
            raise ValidationException(
                "Invalid Script Task.  No Script Provided. " + str(ae),
                node=self.node, file_name=self.filename)

