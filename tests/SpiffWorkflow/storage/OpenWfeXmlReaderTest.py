import sys, unittest, re, os
dirname = os.path.dirname(__file__)
data_dir = os.path.join(dirname, '..', 'data')
sys.path.insert(0, os.path.join(dirname, '..', '..', '..', 'src'))

from PatternTest import track_workflow
from SpiffWorkflow import Workflow
from SpiffWorkflow.storage import OpenWfeXmlReader
from xml.parsers.expat import ExpatError

class OpenWfeXmlReaderTest(unittest.TestCase):
    def setUp(self):
        self.reader = OpenWfeXmlReader()

    def on_reached_cb(self, workflow, instance):
        on_reached_cb(workflow, instance, [])
        instance.set_attribute(test_attribute1 = 'false')
        instance.set_attribute(test_attribute2 = 'true')
        return True

    def testParseString(self):
        self.assertRaises(ExpatError,
                          self.reader.parse_string,
                          '')
        self.reader.parse_string('<xml></xml>')

    def testParseFile(self):
        # File not found.
        self.assertRaises(IOError,
                          self.reader.parse_file,
                          'foo')

        # 0 byte sized file.
        self.assertRaises(ExpatError,
                          self.reader.parse_file,
                          os.path.join(data_dir, 'empty1.xml'))

        # File containing only "<xml></xml>".
        self.reader.parse_file(os.path.join(data_dir, 'empty2.xml'))

        # Read a complete workflow.
        self.reader.parse_file(os.path.join(data_dir, 'openwfe/workflow1.xml'))

    def testRunWorkflow(self):
        xml_file      = os.path.join(data_dir, 'openwfe/workflow1.xml')
        path_file     = os.path.splitext(xml_file)[0] + '.path'
        expected_path = open(path_file).read().strip().split('\n')
        wf_specs      = self.reader.parse_file(xml_file)
        wf_spec       = wf_specs[0]
        taken_path    = track_workflow(wf_spec)
        workflow      = Workflow(wf_spec)
        try:
            workflow.complete_all()
        except:
            workflow.dump()
            raise

        if taken_path != expected_path:
            for taken, expected in zip(taken_path, expected_path):
                print "TAKEN:   ", taken
                print "EXPECTED:", expected
        self.assertEqual(expected_path, taken_path)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(OpenWfeXmlReaderTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
