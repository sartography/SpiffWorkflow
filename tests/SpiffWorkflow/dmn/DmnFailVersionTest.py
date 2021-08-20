import unittest
from os import listdir
from os.path import dirname, isfile, join

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser
from SpiffWorkflow.dmn.parser.DMNParser import DMNParser
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase


class DmnVersionTest(BpmnWorkflowTestCase):
    PARSER_CLASS = BpmnDmnParser

    def _assert_parse_all_pass(self, dir_path: str):
        dir_name = join(dirname(__file__), 'data', 'dmn_version_test', dir_path)
        dmn_files = [join(dir_name, f) for f in listdir(dir_name) if f.endswith('.dmn') and isfile(join(dir_name, f))]
        self.assertGreater(len(dmn_files), 0)
        self.parser.add_dmn_files(dmn_files)

        parser: DMNParser
        for parser in self.parser.dmn_parsers.values():
            parser.parse()
            self.assertIsNotNone(parser.get_id())
            self.assertIsNotNone(parser.get_name())

    def _assert_parse_all_fail(self, dir_path: str):
        dir_name = join(dirname(__file__), 'data', 'dmn_version_test', dir_path)
        dmn_files = [join(dir_name, f) for f in listdir(dir_name) if f.endswith('.dmn') and isfile(join(dir_name, f))]
        self.assertGreater(len(dmn_files), 0)
        with self.assertRaises(IndexError):
            self.parser.add_dmn_files(dmn_files)

    def setUp(self):
        self.parser = BpmnDmnParser()

    def testLoadV1_2_supported(self):
        self._assert_parse_all_pass('v1_2_supported')

    def testLoadV1_2_unsupported(self):
        self._assert_parse_all_fail('v1_2_unsupported')

    def testLoadV1_3_supported(self):
        self._assert_parse_all_pass('v1_3_supported')

    def testLoadV1_3_unsupported(self):
        self._assert_parse_all_fail('v1_3_unsupported')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DmnVersionTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
