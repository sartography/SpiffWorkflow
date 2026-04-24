import unittest
from types import SimpleNamespace

from SpiffWorkflow.bpmn.parser.event_parsers import EventDefinitionParser
from SpiffWorkflow.bpmn.specs.event_definitions.message import CorrelationProperty


class FakeNode:
    def __init__(self, attrib=None, text=None, parent=None, children=None):
        self.attrib = attrib or {}
        self.text = text
        self._parent = parent
        self._children = children or []

    def get(self, key, default=None):
        return self.attrib.get(key, default)

    def getparent(self):
        return self._parent

    def getchildren(self):
        return list(self._children)


class EventParserTest(unittest.TestCase):
    def _parser(self):
        parser = EventDefinitionParser.__new__(EventDefinitionParser)
        parser.filename = "test.bpmn"
        parser.node = FakeNode({"id": "Task_1", "name": "Task"})
        parser.process_parser = SimpleNamespace(
            parser=SimpleNamespace(
                messages={"message_1": "Message 1"},
                message_correlations={
                    "message_1": [CorrelationProperty("prop_1", "payload.value", ["Conversation 1"])]
                },
                signals={"signal_1": "Signal 1"},
                errors={"error_1": {"name": "Error 1", "error_code": "E-1"}},
                escalations={"escalation_1": {"name": "Escalation 1", "escalation_code": "ESC-1"}},
            )
        )
        parser.get_event_description = lambda event: "Event Description"
        parser.raise_validation_exception = lambda message, node=None: (_ for _ in ()).throw(AssertionError(message))
        parser.doc_xpath_count = 0

        def doc_xpath(path):
            parser.doc_xpath_count += 1
            if path == './/bpmn:message[@id="message_1"]':
                return [FakeNode({"id": "message_1", "name": "Message 1"})]
            if path == ".//bpmn:correlationPropertyRetrievalExpression[@messageRef='message_1']":
                correlation_key = FakeNode({"id": "prop_1", "name": "Conversation 1"})
                return [
                    FakeNode(
                        {"messageRef": "message_1"},
                        parent=correlation_key,
                        children=[FakeNode(text="payload.value")],
                    )
                ]
            if path == ".//bpmn:correlationKey/bpmn:correlationPropertyRef[text()='prop_1']":
                return [FakeNode(text="prop_1", parent=FakeNode({"name": "Conversation 1"}))]
            if path == './/bpmn:signal[@id="signal_1"]':
                return [FakeNode({"id": "signal_1", "name": "Signal 1"})]
            if path == './/bpmn:error[@id="error_1"]':
                return [FakeNode({"id": "error_1", "name": "Error 1", "errorCode": "E-1"})]
            if path == './/bpmn:escalation[@id="escalation_1"]':
                return [FakeNode({"id": "escalation_1", "name": "Escalation 1", "escalationCode": "ESC-1"})]
            return []

        parser.doc_xpath = doc_xpath
        return parser

    def testIndexedMessageDefinitionsAvoidDocumentXPathLookups(self):
        parser = self._parser()

        message_event = FakeNode({"messageRef": "message_1"}, parent=FakeNode({"name": "Parent Event"}))
        event_definition = parser.parse_message_event(message_event)

        self.assertEqual("Message 1", event_definition.name)
        self.assertEqual(["Conversation 1"], event_definition.correlation_properties[0].correlation_keys)
        self.assertEqual(0, parser.doc_xpath_count)

    def testIndexedSignalErrorAndEscalationAvoidDocumentXPathLookups(self):
        parser = self._parser()

        signal = parser.parse_signal_event(FakeNode({"signalRef": "signal_1"}, parent=FakeNode({"name": "Parent Event"})))
        error = parser.parse_error_event(FakeNode({"errorRef": "error_1"}))
        escalation = parser.parse_escalation_event(FakeNode({"escalationRef": "escalation_1"}))

        self.assertEqual("Signal 1", signal.name)
        self.assertEqual("Error 1", error.name)
        self.assertEqual("E-1", error.code)
        self.assertEqual("Escalation 1", escalation.name)
        self.assertEqual("ESC-1", escalation.code)
        self.assertEqual(0, parser.doc_xpath_count)
