import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

import pickle
import pprint
from random import randint
from WorkflowTest import WorkflowTest, \
                         on_reached_cb, \
                         on_complete_cb, \
                         assert_same_path
from SpiffWorkflow import Workflow
from SpiffWorkflow.storage import XmlReader

class PersistenceTest(WorkflowTest):
    def setUp(self):
        WorkflowTest.setUp(self)
        self.reader     = XmlReader()
        self.data_file  = 'data.pkl'
        self.taken_path = None

    def doPickleSingle(self, workflow):
        self.taken_path = {'reached':   [],
                           'completed': []}
        for name, task in workflow.spec.task_specs.iteritems():
            task.reached_event.connect(on_reached_cb,
                                       self.taken_path['reached'])
            task.completed_event.connect(on_complete_cb,
                                         self.taken_path['completed'])

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
        # copy of self.taken_path.
        for name, task in workflow.spec.task_specs.iteritems():
            task.reached_event.disconnect(on_reached_cb)
            task.completed_event.disconnect(on_complete_cb)
            task.reached_event.connect(on_reached_cb,
                                       self.taken_path['reached'])
            task.completed_event.connect(on_complete_cb,
                                         self.taken_path['completed'])

        # Run the rest of the workflow.
        workflow.complete_all()
        after = workflow.get_dump()
        self.assert_(workflow.is_completed(), 'Workflow not complete:' + after)
        assert_same_path(self,
                         self.expected_path,
                         self.taken_path['completed'])

    def testPickle(self):
        # Read a complete workflow.
        file = os.path.join(os.path.dirname(__file__), 'data/spiff-xml/workflow1.xml')

        for i in xrange(5):
            wf_spec_list = self.reader.parse_file(file)
            wf_spec      = wf_spec_list[0]
            workflow     = Workflow(wf_spec)
            self.doPickleSingle(workflow)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PersistenceTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
