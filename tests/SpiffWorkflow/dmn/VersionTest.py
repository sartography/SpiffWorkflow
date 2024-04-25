import unittest
import os

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser

data_dir = os.path.join(os.path.dirname(__file__), 'data', 'dmn_version_test')

class DmnVersionTest(unittest.TestCase):

    def setUp(self):
        self.parser = BpmnDmnParser()
        self.parser.namespaces.update({'dmn': 'https://www.omg.org/spec/DMN/20191111/MODEL/'})

    def test_load_v1_0(self):
        filename = os.path.join(data_dir, 'dmn_version_20151101_test.dmn')
        self.parser.add_dmn_file(filename)

    def test_load_v1_1(self):
        filename = os.path.join(data_dir, 'dmn_version_20191111_test.dmn')
        self.parser.add_dmn_file(filename)

    def test_load_v1_2_supported(self):
        self._assert_parse_all_pass('v1_2_supported')

    def test_load_v1_2_unsupported(self):
        self._assert_parse_all_fail('v1_2_unsupported')

    def test_load_v1_3_supported(self):
        self._assert_parse_all_pass('v1_3_supported')

    def test_load_v1_3_unsupported(self):
        self._assert_parse_all_fail('v1_3_unsupported')

    def _assert_parse_all_pass(self, dir_path):
        dirname = os.path.join(data_dir, dir_path)
        self.parser.add_dmn_files_by_glob(f'{dirname}/*.dmn')
        for parser in self.parser.dmn_parsers.values():
            parser.parse()
            self.assertIsNotNone(parser.bpmn_id)
            self.assertIsNotNone(parser.get_name())

    def _assert_parse_all_fail(self, dir_path):
        dirname = os.path.join(data_dir, dir_path)
        with self.assertRaises(IndexError):
            self.parser.add_dmn_files_by_glob(f'{dirname}/*.dmn')
