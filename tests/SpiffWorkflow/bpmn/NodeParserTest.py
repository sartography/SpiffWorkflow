import unittest
from types import SimpleNamespace

from SpiffWorkflow.bpmn.parser.node_parser import NodeParser


class FakeNode:
    def __init__(self, attrib=None, text=None):
        self.attrib = attrib or {}
        self.text = text

    def get(self, key, default=None):
        return self.attrib.get(key, default)


class NodeParserTest(unittest.TestCase):
    def testConstructorSkipsLaneLookupWithoutProcessParser(self):
        class TrackingNodeParser(NodeParser):
            def __init__(self, *args, **kwargs):
                self.get_lane_calls = 0
                super().__init__(*args, **kwargs)

            def _get_lane(self):
                self.get_lane_calls += 1
                return "Lane A"

        parser = TrackingNodeParser(FakeNode({"id": "Task_1"}))

        self.assertIsNone(parser.lane)
        self.assertEqual(0, parser.get_lane_calls)

    def testIndexedDataReferencesAndPositionsAvoidDocumentXPathLookups(self):
        parser = NodeParser.__new__(NodeParser)
        parser.node = FakeNode({"id": "Task_1"})
        parser.filename = "test.bpmn"
        parser.process_parser = SimpleNamespace(
            spec=SimpleNamespace(data_objects={"Data_1": "data-object"}),
            parent=None,
            data_stores={},
            get_data_object_reference=lambda reference_id: FakeNode({"dataObjectRef": "Data_1"}) if reference_id == "Ref_1" else None,
            get_data_store_reference=lambda reference_id: None,
            get_position=lambda node_id: {"x": 10.0, "y": 20.0} if node_id == "Task_1" else {"x": 0.0, "y": 0.0},
            get_lane_name=lambda node_id: "Lane A" if node_id == "Task_1" else None,
        )
        parser.xpath = lambda path: [FakeNode(text="Ref_1")]
        parser.doc_xpath_count = 0

        def doc_xpath(path):
            parser.doc_xpath_count += 1
            return []

        parser.doc_xpath = doc_xpath

        self.assertEqual(["data-object"], parser.parse_incoming_data_references())
        self.assertEqual(["data-object"], parser.parse_outgoing_data_references())
        self.assertEqual({"x": 10.0, "y": 20.0}, parser.get_position())
        self.assertEqual("Lane A", parser._get_lane())
        self.assertEqual(0, parser.doc_xpath_count)

    def testIndexedEmptyLaneAndPositionAvoidFallbackDocumentXPathLookups(self):
        parser = NodeParser.__new__(NodeParser)
        parser.node = FakeNode({"id": "Task_1"})
        parser.filename = "test.bpmn"
        parser.process_parser = SimpleNamespace(
            positions_by_node_id={},
            lanes_by_node_id={},
            get_position=lambda node_id: {"x": 0.0, "y": 0.0},
            get_lane_name=lambda node_id: None,
        )
        parser.doc_xpath_count = 0

        def doc_xpath(path):
            parser.doc_xpath_count += 1
            return []

        parser.doc_xpath = doc_xpath

        self.assertEqual({"x": 0.0, "y": 0.0}, parser.get_position())
        self.assertIsNone(parser._get_lane())
        self.assertEqual(0, parser.doc_xpath_count)
