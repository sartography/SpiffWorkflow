import sys, unittest, re, os
data_dir = os.path.join(os.path.dirname(__file__), 'data')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pickle
import pprint
from random import randint
from util import track_workflow
from SpiffWorkflow import Workflow
from SpiffWorkflow.storage import XmlReader

class PersistenceTest(unittest.TestCase):
    def setUp(self):
        self.reader    = XmlReader()
        self.data_file = 'data.pkl'

    def doPickleSingle(self, workflow, expected_path):
        taken_path = track_workflow(workflow.spec)

        # Execute a random number of steps.
        for i in xrange(randint(0, len(workflow.spec.task_specs))):
            workflow.complete_next()
    
        # Store the workflow instance in a file.
        output = open(self.data_file, 'wb')
        pickle.dump(workflow, output, -1)
        output.close()
        before = workflow.get_dump()

        # Load the workflow instance from a file and delete the file.
        input = open(self.data_file, 'rb')
        workflow = pickle.load(input)
        input.close()
        os.remove(self.data_file)
        after = workflow.get_dump()

        # Make sure that the state of the workflow did not change.
        self.assert_(before == after, 'Before:\n' + before + '\n' \
                                    + 'After:\n'  + after  + '\n')

        # Re-connect signals, because the pickle dump now only contains a 
        # copy of taken_path.
        taken_path = track_workflow(workflow.spec, taken_path)

        # Run the rest of the workflow.
        workflow.complete_all()
        after = workflow.get_dump()
        self.assert_(workflow.is_completed(), 'Workflow not complete:' + after)
        #taken_path = '\n'.join(taken_path) + '\n'
        if taken_path != expected_path:
            for taken, expected in zip(taken_path, expected_path):
                print "TAKEN:   ", taken
                print "EXPECTED:", expected
        self.assertEqual(expected_path, taken_path)

    def testPickle(self):
        # Read a complete workflow.
        xml_file      = os.path.join(data_dir, 'spiff-xml', 'workflow1.xml')
        path_file     = os.path.splitext(xml_file)[0] + '.path'
        expected_path = open(path_file).read().strip().split('\n')
        wf_spec       = self.reader.parse_file(xml_file)[0]

        for i in xrange(5):
            workflow = Workflow(wf_spec)
            self.doPickleSingle(workflow, expected_path)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PersistenceTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
