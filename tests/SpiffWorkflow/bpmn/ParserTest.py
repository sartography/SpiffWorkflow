import unittest
import os

from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser, BpmnValidator
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException


class ParserTest(unittest.TestCase):

    def testIOSpecification(self):

        parser = BpmnParser()
        bpmn_file = os.path.join(os.path.dirname(__file__), 'data', 'io_spec.bpmn')
        parser.add_bpmn_file(bpmn_file)
        spec = parser.get_spec('subprocess')
        self.assertEqual(len(spec.data_inputs), 2)
        self.assertEqual(len(spec.data_outputs), 2)

    def testDataReferences(self):

        parser = BpmnParser()
        bpmn_file = os.path.join(os.path.dirname(__file__), 'data', 'data_object.bpmn')
        parser.add_bpmn_file(bpmn_file)
        spec = parser.get_spec("Process")
        generate = spec.task_specs['generate_data']
        read = spec.task_specs['read_data']
        self.assertEqual(len(generate.data_output_associations), 1)
        self.assertEqual(generate.data_output_associations[0].name, 'obj_1')
        self.assertEqual(len(read.data_input_associations), 1)
        self.assertEqual(read.data_input_associations[0].name, 'obj_1')

    def testValidatorError(self):
        parser = BpmnParser(validator=BpmnValidator())
        bpmn_file = os.path.join(os.path.dirname(__file__), 'data',
                                 'data_object_invalid.bpmn')
        errored = False
        try:
            parser.add_bpmn_file(bpmn_file)
        except ValidationException as ex:
            errored = True
            self.assertEqual(ex.file_name, bpmn_file)
            self.assertEqual(14, ex.line_number)
            self.assertIn('DataObjectReference_0cm8dnh', str(ex))
        assert(errored, "This should have errored out with a validation exception.")
