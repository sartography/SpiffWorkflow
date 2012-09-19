from SpiffWorkflow.bpmn.specs.CallActivity import CallActivity
from SpiffWorkflow.bpmn.specs.EndEvent import EndEvent
from SpiffWorkflow.bpmn.specs.ExclusiveGateway import ExclusiveGateway
from SpiffWorkflow.bpmn.specs.UserTask import UserTask
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.parser.task_parsers import UserTaskParser, EndEventParser, CallActivityParser
from SpiffWorkflow.bpmn.parser.util import full_tag
from SpiffWorkflow.operators import Assign

__author__ = 'matth'

#This provides some extensions to the BPMN parser that make it easier to implement testcases

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
        task.set_attribute(choice=choice)
        task.complete()

class TestEndEvent(EndEvent):

    def _on_complete_hook(self, my_task):
        my_task.set_attribute(end_event=self.description)
        super(TestEndEvent, self)._on_complete_hook(my_task)

class TestCallActivity(CallActivity):

    def __init__(self, parent, name, **kwargs):
        super(TestCallActivity, self).__init__(parent, name, out_assign=[Assign('choice', 'end_event')], **kwargs)

class TestBpmnParser(BpmnParser):
    OVERRIDE_PARSER_CLASSES = {
        full_tag('userTask')            : (UserTaskParser, TestUserTask),
        full_tag('endEvent')            : (EndEventParser, TestEndEvent),
        full_tag('callActivity')        : (CallActivityParser, TestCallActivity),
        }

    def parse_condition(self, condition_expression, outgoing_task, outgoing_task_node, sequence_flow_node, condition_expression_node):
        cond = super(TestBpmnParser, self).parse_condition(condition_expression,outgoing_task, outgoing_task_node, sequence_flow_node, condition_expression_node)
        if cond is not None:
            return cond
        return "choice == '%s'" % sequence_flow_node.get('name', None)
