import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from WorkflowTest import on_reached_cb, on_complete_cb, assert_same_path
from SpiffWorkflow import Workflow
from SpiffWorkflow.storage import OpenWfeXmlReader
from xml.parsers.expat import ExpatError

class OpenWfeXmlReaderTest(unittest.TestCase):
    def setUp(self):
        self.reader     = OpenWfeXmlReader()
        self.taken_path = []


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
                          os.path.join(os.path.dirname(__file__), 'data/empty1.xml'))

        # File containing only "<xml></xml>".
        self.reader.parse_file(os.path.join(os.path.dirname(__file__), 'data/empty2.xml'))

        # Read a complete workflow.
        self.reader.parse_file(os.path.join(os.path.dirname(__file__), 'data/openwfe/workflow1.xml'))


    def testRunWorkflow(self):
        filename = os.path.join(os.path.dirname(__file__), 'data/openwfe/workflow1.xml')
        wf_specs = self.reader.parse_file(filename)
        wf_spec = wf_specs[0]

        for name in wf_spec.task_specs:
            wf_spec.task_specs[name].reached_event.connect(self.on_reached_cb)
            wf_spec.task_specs[name].completed_event.connect(on_complete_cb, self.taken_path)

        workflow = Workflow(wf_spec)
        try:
            workflow.complete_all()
        except:
            workflow.dump()
            raise

        path = [( 1, 'Start'),
                ( 2, 'concurrence_1'),
                ( 3, 'task_a1'),
                ( 4, 'task_a2'),
                ( 5, 'if_condition_1'),
                ( 6, 'task_a3'),
                ( 7, 'if_condition_1_end'),
                ( 8, 'if_condition_2'),
                ( 9, 'task_a5'),
                (10, 'if_condition_2_end'),
                ( 3, 'task_b1'),
                ( 4, 'task_b2'),
                ( 5, 'concurrence_1_end'),
                ( 6, 'task_c1'),
                ( 7, 'task_c2'),
                ( 8, 'End')]

        assert_same_path(self, path, self.taken_path)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(OpenWfeXmlReaderTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
