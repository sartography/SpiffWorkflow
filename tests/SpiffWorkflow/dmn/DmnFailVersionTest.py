import unittest
import os

from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser


class DmnVersionTest(unittest.TestCase):

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

    def _assert_parse_all_pass(self, dir_path):
        dirname = os.path.join(os.path.dirname(__file__), 'data', 'dmn_version_test', dir_path)
        self.parser.add_dmn_files_by_glob(f'{dirname}/*.dmn')
        for parser in self.parser.dmn_parsers.values():
            parser.parse()
            self.assertIsNotNone(parser.get_id())
            self.assertIsNotNone(parser.get_name())

    def _assert_parse_all_fail(self, dir_path):
        dirname = os.path.join(os.path.dirname(__file__), 'data', 'dmn_version_test', dir_path)
        with self.assertRaises(IndexError):
            self.parser.add_dmn_files_by_glob(f'{dirname}/*.dmn')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(DmnVersionTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
