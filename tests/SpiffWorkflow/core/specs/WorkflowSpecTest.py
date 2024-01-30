import unittest
import os
import pickle
from lxml import etree

from random import randint

from SpiffWorkflow import Workflow
from SpiffWorkflow.specs import Join, WorkflowSpec
from SpiffWorkflow.serializer.prettyxml import XmlSerializer

from ..util import track_workflow

data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')

serializer = XmlSerializer()
data_file = 'data.pkl'


class WorkflowSpecTest(unittest.TestCase):

    def setUp(self):
        self.wf_spec = WorkflowSpec(addstart=True)

    def testConstructor(self):
        spec = WorkflowSpec('my spec', addstart=True)
        self.assertEqual('my spec', spec.name)

    def testGetTaskSpecFromName(self):
        pass  # FIXME

    def testGetDump(self):
        pass  # FIXME

    def testDump(self):
        pass  # FIXME

    def doPickleSingle(self, workflow, expected_path):
        taken_path = track_workflow(workflow.spec)

        # Execute a random number of steps.
        for i in range(randint(0, len(workflow.spec.task_specs))):
            workflow.run_next()

        # Store the workflow instance in a file.
        with open(data_file, 'wb') as fp:
            pickle.dump(workflow, fp, -1)
        before = workflow.get_dump()

        # Load the workflow instance from a file and delete the file.
        with open(data_file, 'rb') as fp:
            workflow = pickle.load(fp)
        os.remove(data_file)
        after = workflow.get_dump()

        # Make sure that the state of the workflow did not change.
        self.assertEqual(before, after)

        # Re-connect signals, because the pickle dump now only contains a
        # copy of taken_path.
        taken_path = track_workflow(workflow.spec, taken_path)

        # Run the rest of the workflow.
        workflow.run_all()
        after = workflow.get_dump()
        self.assertTrue(workflow.is_completed(), 'Workflow not complete:' + after)
        self.assertEqual(expected_path, taken_path)

    def testSerialize(self):
        # Read a complete workflow spec.
        xml_file = os.path.join(data_dir, 'workflow1.xml')
        with open(xml_file) as fp:
            xml = etree.parse(fp).getroot()
        path_file = os.path.splitext(xml_file)[0] + '.path'
        with open(path_file) as fp:
            expected_path = fp.read().strip().split('\n')
        wf_spec = WorkflowSpec.deserialize(serializer, xml)

        for i in range(5):
            workflow = Workflow(wf_spec)
            self.doPickleSingle(workflow, expected_path)

    def testValidate(self):
        """
        Tests that we can detect when two wait tasks are waiting on each
        other.
        """
        task1 = Join(self.wf_spec, 'First')
        self.wf_spec.start.connect(task1)
        task2 = Join(self.wf_spec, 'Second')
        task1.connect(task2)

        task1.connect(task2)
        task2.connect(task1)

        results = self.wf_spec.validate()
        self.assertIn("Found loop with 'Second': Second->First then 'Second' "
                      "again", results)
        self.assertIn("Found loop with 'First': First->Second then 'First' "
                      "again", results)

    def testGetTaskSpecFromId(self):
        pass

