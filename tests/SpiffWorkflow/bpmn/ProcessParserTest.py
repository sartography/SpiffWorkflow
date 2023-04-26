import io
import os
import unittest

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.parser.ProcessParser import ProcessParser

def _process_parser(bpmn_filename, process_id):
    parser = BpmnParser()
    bpmn_file = os.path.join(os.path.dirname(__file__), 'data', bpmn_filename)
    parser.add_bpmn_file(bpmn_file)
    return parser.get_process_parser(process_id)

class ProcessParserTest(unittest.TestCase):
    def testReturnsEmptyListIfNoCallActivities(self):
        parser = _process_parser("no-tasks.bpmn", "no_tasks")
        assert parser.called_element_ids() == []
    
    def testHandlesSingleCallActivity(self):
        parser = _process_parser("single_call_activity.bpmn", "Process_p4pfxhq")
        assert parser.called_element_ids() == ["SingleTask_Process"]
    
    def testHandlesMultipleCallActivities(self):
        parser = _process_parser("multiple_call_activities.bpmn", "Process_90mmqlw")
        assert parser.called_element_ids() == ["Process_sypm122", "Process_diu8ta2", "Process_l14lar1"]
    
    def testCanAddDmnFromString(self):
        parser = BpmnDmnParser()
        parser.add_dmn_str(EMPTY_DMN)
        assert len(parser.dmn_parsers) > 0
    
    def testCanAddDmnFromFileLikeObject(self):
        parser = BpmnDmnParser()
        parser.add_dmn_io(io.StringIO(EMPTY_DMN))
        assert len(parser.dmn_parsers) > 0
    
    def testCanAddBpmnFromString(self):
        parser = BpmnParser()
        parser.add_bpmn_str(EMPTY_WORKFLOW)
        assert parser.get_spec("no_tasks") is not None
    
    def testCanAddBpmnFromFileLikeObject(self):
        parser = BpmnParser()
        parser.add_bpmn_io(io.StringIO(EMPTY_WORKFLOW))
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

EMPTY_DMN = """
<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/" xmlns:dmndi="https://www.omg.org/spec/DMN/20191111/DMNDI/" xmlns:dc="http://www.omg.org/spec/DMN/20180521/DC/" id="Definitions_76910d7" name="DRD" namespace="http://camunda.org/schema/1.0/dmn">
  <decision id="decision_1" name="Decision 1">
    <decisionTable id="decisionTable_1">
      <input id="input_1" label="First Name">
        <inputExpression id="inputExpression_1" typeRef="string">
          <text></text>
        </inputExpression>
      </input>
      <output id="output_1" label="Last Name" typeRef="string" />
    </decisionTable>
  </decision>
</definitions>
"""
