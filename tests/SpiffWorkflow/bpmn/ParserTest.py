import unittest
import os

from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException


class ParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = BpmnParser()

    def testIOSpecification(self):

        bpmn_file = os.path.join(os.path.dirname(__file__), 'data', 'io_spec.bpmn')
        self.parser.add_bpmn_file(bpmn_file)
        spec = self.parser.get_spec('subprocess')
        self.assertEqual(len(spec.io_specification.data_inputs), 2)
        self.assertEqual(len(spec.io_specification.data_outputs), 2)

    def testDataReferences(self):

        bpmn_file = os.path.join(os.path.dirname(__file__), 'data', 'data_object.bpmn')
        self.parser.add_bpmn_file(bpmn_file)
        spec = self.parser.get_spec("Process")
        generate = spec.task_specs['generate_data']
        read = spec.task_specs['read_data']
        self.assertEqual(len(generate.data_output_associations), 1)
        self.assertEqual(generate.data_output_associations[0].bpmn_id, 'obj_1')
        self.assertEqual(len(read.data_input_associations), 1)
        self.assertEqual(read.data_input_associations[0].bpmn_id, 'obj_1')

    def testSkipSubprocesses(self):

        bpmn_file = os.path.join(os.path.dirname(__file__), 'data', 'call_activity_end_event.bpmn')
        self.parser.add_bpmn_file(bpmn_file)
        # The default is to require that call activity specs be included, so this should raise an exception
        self.assertRaises(ValidationException, self.parser.get_subprocess_specs, 'Process_8200379')
        # When call activity specs are skipped, no exception should be raised
        subprocess_specs = self.parser.get_subprocess_specs('Process_8200379', require_call_activity_specs=False)
        self.assertDictEqual(subprocess_specs, {'Call_Activity_Get_Data': None})

    def testInvalidProcessID(self):
        bpmn_file = os.path.join(os.path.dirname(__file__), 'data', 'call_activity_end_event.bpmn')
        self.parser.add_bpmn_file(bpmn_file)
        self.assertRaisesRegex(
            ValidationException, "The process '\w+' was not found*",
            self.parser.get_spec, "Process")
