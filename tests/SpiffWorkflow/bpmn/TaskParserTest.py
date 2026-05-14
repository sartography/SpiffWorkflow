import unittest
from types import SimpleNamespace

from lxml import etree

from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser


class FakeTask:
    def __init__(self, name="task"):
        self.name = name
        self.extensions = {}

    def connect(self, other):
        return None


class IndexedTaskParser(TaskParser):
    def create_task(self):
        return FakeTask(self.bpmn_id)

    def connect_outgoing(self, outgoing_task, sequence_flow_node, is_default):
        return None

    def get_position(self, node=None):
        return {"x": 0.0, "y": 0.0}


class TaskParserTest(unittest.TestCase):
    def testParseNodeAvoidsDocumentXPathForOutgoingLookupsWhenIndexed(self):
        process = etree.fromstring(
            """
            <bpmn:process xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" id="Process_1" isExecutable="true">
              <bpmn:task id="Task_1" name="First" />
              <bpmn:task id="Task_2" name="Second" />
              <bpmn:sequenceFlow id="Flow_1" sourceRef="Task_1" targetRef="Task_2" />
            </bpmn:process>
            """
        )
        task_node = process.xpath('./bpmn:task', namespaces={'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'})[0]
        target_node = process.xpath('./bpmn:task', namespaces={'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'})[1]
        sequence_flow = process.xpath('./bpmn:sequenceFlow', namespaces={'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL'})[0]

        process_parser = SimpleNamespace(
            spec=SimpleNamespace(task_specs={}),
            filename="test.bpmn",
            parser=SimpleNamespace(spec_descriptions={}),
            parse_node=lambda node: FakeTask(node.get("id")),
            get_lane_name=lambda node_id: None,
            get_boundary_events=lambda attached_to_ref: [],
            get_outgoing_sequence_flows=lambda source_ref: [sequence_flow],
            get_node_by_id=lambda node_id: target_node if node_id == "Task_2" else None,
        )

        parser = IndexedTaskParser(process_parser, FakeTask, task_node)
        parser.doc_xpath_count = 0
        original_doc_xpath = parser.doc_xpath

        def counting_doc_xpath(path):
            parser.doc_xpath_count += 1
            return original_doc_xpath(path)

        parser.doc_xpath = counting_doc_xpath
        parser.parse_node()

        self.assertEqual(0, parser.doc_xpath_count)
