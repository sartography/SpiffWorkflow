from copy import deepcopy

from SpiffWorkflow.bpmn.specs.data_spec import BpmnDataStoreSpecification
from SpiffWorkflow.bpmn.specs.defaults import ExclusiveGateway, UserTask
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser
from SpiffWorkflow.bpmn.parser.task_parsers import ConditionalGatewayParser
from SpiffWorkflow.bpmn.parser.util import full_tag

from SpiffWorkflow.bpmn.serializer.helpers.bpmn_converter import BpmnConverter
from SpiffWorkflow.bpmn.serializer.default.task_spec import BpmnTaskSpecConverter
from SpiffWorkflow.bpmn.serializer import DEFAULT_CONFIG


__author__ = 'matth'

# One glorious day I will be able to remove these classes.


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
        task.run()


class TestExclusiveGatewayParser(ConditionalGatewayParser):

    def parse_condition(self, sequence_flow_node):
        cond = super().parse_condition(sequence_flow_node)
        if cond is not None:
            return cond
        return "choice == '%s'" % sequence_flow_node.get('name', None)

class TestDataStore(BpmnDataStoreSpecification):

    _value = None

    def get(self, my_task):
        """Copy a value from a data store into task data."""
        my_task.data[self.bpmn_id] = TestDataStore._value

    def set(self, my_task):
        """Copy a value from the task data to the data store"""
        TestDataStore._value = my_task.data[self.bpmn_id]
        del my_task.data[self.bpmn_id]

class TestDataStoreConverter(BpmnConverter):

    def to_dict(self, spec):
        return {
            "bpmn_id": spec.bpmn_id,
            "bpmn_name": spec.bpmn_name,
            "capacity": spec.capacity,
            "is_unlimited": spec.is_unlimited,
            "_value": TestDataStore._value,
        }

    def from_dict(self, dct):
        _value = dct.pop("_value")
        data_store = TestDataStore(**dct)
        TestDataStore._value = _value
        return data_store

class TestBpmnParser(BpmnParser):
    OVERRIDE_PARSER_CLASSES = {
        full_tag('userTask'): (TaskParser, TestUserTask),
        full_tag('exclusiveGateway'): (TestExclusiveGatewayParser, ExclusiveGateway),
    }

    DATA_STORE_CLASSES = {
        "TestDataStore": TestDataStore,
    }

SERIALIZER_CONFIG = deepcopy(DEFAULT_CONFIG)
SERIALIZER_CONFIG[TestUserTask] = BpmnTaskSpecConverter
SERIALIZER_CONFIG[TestDataStore] = TestDataStoreConverter
