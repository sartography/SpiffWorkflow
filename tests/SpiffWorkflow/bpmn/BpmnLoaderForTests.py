# -*- coding: utf-8 -*-

from SpiffWorkflow.bpmn.specs.ExclusiveGateway import ExclusiveGateway
from SpiffWorkflow.bpmn.specs.UserTask import UserTask
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser
from SpiffWorkflow.bpmn.parser.task_parsers import ConditionalGatewayParser
from SpiffWorkflow.bpmn.parser.util import full_tag

from SpiffWorkflow.bpmn.serializer.bpmn_converters import BpmnTaskSpecConverter

# Many of our tests relied on the Packager to set the calledElement attribute on
# Call Activities.  I've moved that code to a customized parser.
from SpiffWorkflow.signavio.parser.tasks import CallActivityParser
from SpiffWorkflow.bpmn.specs.SubWorkflowTask import CallActivity

__author__ = 'matth'

# This provides some extensions to the BPMN parser that make it easier to
# implement testcases


class TestUserTask(UserTask):

    def get_user_choices(self):
        if not self.outputs:
            return []
        assert len(self.outputs) == 1
        next_node = self.outputs[0]
        if isinstance(next_node, ExclusiveGateway):
            return next_node.get_outgoing_sequence_names()
        return self.get_outgoing_sequence_names()

    def do_choice(self, task, choice):
        task.set_data(choice=choice)
        task.complete()

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_generic(wf_spec, s_state, TestUserTask)

class TestExclusiveGatewayParser(ConditionalGatewayParser):

    def parse_condition(self, sequence_flow_node):
        cond = super().parse_condition(sequence_flow_node)
        if cond is not None:
            return cond
        return "choice == '%s'" % sequence_flow_node.get('name', None)

class TestUserTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None):
        super().__init__(TestUserTask, data_converter)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        return dct

    def from_dict(self, dct):
        return self.task_spec_from_dict(dct)


class TestBpmnParser(BpmnParser):
    OVERRIDE_PARSER_CLASSES = {
        full_tag('userTask'): (TaskParser, TestUserTask),
        full_tag('exclusiveGateway'): (TestExclusiveGatewayParser, ExclusiveGateway),
        full_tag('callActivity'): (CallActivityParser, CallActivity)
    }

