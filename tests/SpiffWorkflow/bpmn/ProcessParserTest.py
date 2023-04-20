import os
import unittest

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
