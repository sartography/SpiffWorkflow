import io
import os
import unittest

from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser

class InMemoryBpmnParserTest(unittest.TestCase):
    
    def testCanAddBpmnFromString(self):
        parser = BpmnParser()
        parser.add_bpmn_str(EMPTY_WORKFLOW)
        assert parser.get_spec("no_tasks") is not None
    
    def testCanAddBpmnFromFileLikeObject(self):
        parser = BpmnParser()
        parser.add_bpmn_file_like_object(io.StringIO(EMPTY_WORKFLOW))
        assert parser.get_spec("no_tasks") is not None


EMPTY_WORKFLOW = """
<bpmn:definitions xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" xmlns:di="http://www.omg.org/spec/DD/20100524/DI" id="Definitions_96f6665" targetNamespace="http://bpmn.io/schema/bpmn" exporter="Camunda Modeler" exporterVersion="3.0.0-dev">
  <bpmn:process id="no_tasks" name="No Tasks" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1">
      <bpmn:outgoing>Flow_184umot</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:endEvent id="Event_0qq9il3">
      <bpmn:incoming>Flow_184umot</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:sequenceFlow id="Flow_184umot" sourceRef="StartEvent_1" targetRef="Event_0qq9il3" />
  </bpmn:process>
</bpmn:definitions>
"""
