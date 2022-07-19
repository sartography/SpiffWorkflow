import unittest
import os

from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser


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
