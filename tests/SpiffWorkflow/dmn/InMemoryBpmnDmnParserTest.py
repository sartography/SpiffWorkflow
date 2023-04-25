import io
import os
import unittest

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser

class InMemoryBpmnDmnParserTest(unittest.TestCase):
    
    def testCanAddDmnFromString(self):
        parser = BpmnDmnParser()
        parser.add_dmn_str(EMPTY_DMN)
        assert parser.dmn_parsers
    
    def testCanAddDmnFromFileLikeObject(self):
        parser = BpmnDmnParser()
        parser.add_dmn_file_like_object(io.StringIO(EMPTY_DMN))
        assert parser.dmn_parsers


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
