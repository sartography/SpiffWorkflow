import sys, unittest, re, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from SpiffWorkflow.specs import *
from SpiffWorkflow import Task
from SpiffWorkflow.storage import XmlSerializer
from xml.parsers.expat import ExpatError
from util import run_workflow

class PatternTest(unittest.TestCase):
    def setUp(self):
        Task.id_pool = 0
        Task.thread_id_pool = 0
        self.xml_path = ['data/spiff/control-flow',
                         'data/spiff/data',
                         'data/spiff/resource',
                         'data/spiff']
        self.serializer = XmlSerializer()

    def run_pattern(self, filename):
        # Load the .path file.
        path_file = os.path.splitext(filename)[0] + '.path'
        if os.path.exists(path_file):
            expected_path = open(path_file).read()
        else:
            expected_path = None

        # Load the .data file.
        data_file = os.path.splitext(filename)[0] + '.data'
        if os.path.exists(data_file):
            expected_data = open(data_file, 'r').read()
        else:
            expected_data = None

        # Test patterns that are defined in XML format.
        if filename.endswith('.xml'):
            xml     = open(filename).read()
            wf_spec = WorkflowSpec.deserialize(self.serializer, xml, filename = filename)
            run_workflow(self, wf_spec, expected_path, expected_data)

        # Test patterns that are defined in Python.
        if filename.endswith('.py') and not filename.endswith('__.py'):
            code    = compile(open(filename).read(), filename, 'exec')
            thedict = {}
            result  = eval(code, thedict)
            wf_spec = thedict['TestWorkflowSpec']()
            run_workflow(self, wf_spec, expected_path, expected_data)

    def testPattern(self):
        for basedir in self.xml_path:
            dirname = os.path.join(os.path.dirname(__file__), basedir)

            for filename in os.listdir(dirname):
                if not filename.endswith(('.xml', '.py')):
                    continue
                filename = os.path.join(dirname, filename)
                print filename
                self.run_pattern(filename)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PatternTest)
if __name__ == '__main__':
    if len(sys.argv) == 2:
        test = PatternTest('run_pattern')
        test.setUp()
        test.run_pattern(sys.argv[1])
        sys.exit(0)
    unittest.TextTestRunner(verbosity = 2).run(suite())
