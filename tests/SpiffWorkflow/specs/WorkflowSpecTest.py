import os
import sys
import unittest
data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import pickle
from random import randint
try:
    from util import track_workflow
except ImportError, e:
    from tests.SpiffWorkflow.util import track_workflow
from SpiffWorkflow import Workflow
from SpiffWorkflow.specs import Join, WorkflowSpec
from SpiffWorkflow.storage import XmlSerializer

serializer = XmlSerializer()
data_file = 'data.pkl'

class WorkflowSpecTest(unittest.TestCase):
    CORRELATE = WorkflowSpec

    def setUp(self):
        self.wf_spec = WorkflowSpec()

    def testConstructor(self):
        spec = WorkflowSpec('my spec')
        self.assertEqual('my spec', spec.name)

    def testGetTaskSpecFromName(self):
        pass #FIXME

    def doPickleSingle(self, workflow, expected_path):
        taken_path = track_workflow(workflow.spec)

        # Execute a random number of steps.
        for i in xrange(randint(0, len(workflow.spec.task_specs))):
            workflow.complete_next()

        # Store the workflow instance in a file.
        output = open(data_file, 'wb')
        pickle.dump(workflow, output, -1)
        output.close()
        before = workflow.get_dump()

        # Load the workflow instance from a file and delete the file.
        input = open(data_file, 'rb')
        workflow = pickle.load(input)
        input.close()
        os.remove(data_file)
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

    def testSerialize(self):
        # Read a complete workflow spec.
        xml_file      = os.path.join(data_dir, 'spiff', 'workflow1.xml')
        xml           = open(xml_file).read()
        path_file     = os.path.splitext(xml_file)[0] + '.path'
        expected_path = open(path_file).read().strip().split('\n')
        wf_spec       = WorkflowSpec.deserialize(serializer, xml)

        for i in xrange(5):
            workflow = Workflow(wf_spec)
            self.doPickleSingle(workflow, expected_path)

    def testValidate(self):
        """
        Tests that we can detect when two wait taks are waiting on each
        other.
        """
        task1 = Join(self.wf_spec, 'First')
        self.wf_spec.start.connect(task1)
        task2 = Join(self.wf_spec, 'Second')
        task1.connect(task2)

        task2.follow(task1)
        task1.follow(task2)

        results = self.wf_spec.validate()
        self.assert_("Found loop with 'Second': Second->First then 'Second' "
                "again" in results)
        self.assert_("Found loop with 'First': First->Second then 'First' "
                "again" in results)


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(WorkflowSpecTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
