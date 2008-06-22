import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def suite():
    tests = ['testPickle']
    return unittest.TestSuite(map(PersistenceTest, tests))

import pickle, pprint
from random                import randint
from WorkflowTest          import WorkflowTest, \
                                  on_reached_cb, \
                                  on_complete_cb, \
                                  assert_same_path
from SpiffWorkflow         import Job
from SpiffWorkflow.Storage import XmlReader

class PersistenceTest(WorkflowTest):
    def setUp(self):
        WorkflowTest.setUp(self)
        self.reader     = XmlReader()
        self.data_file  = 'data.pkl'
        self.taken_path = None


    def testPickleSingle(self, workflow, job):
        self.taken_path = {'reached':   [],
                           'completed': []}
        for name, task in workflow.tasks.iteritems():
            task.signal_connect('reached',
                                on_reached_cb,
                                self.taken_path['reached'])
            task.signal_connect('completed',
                                on_complete_cb,
                                self.taken_path['completed'])

        # Execute a random number of steps.
        for i in xrange(randint(0, len(workflow.tasks))):
            job.complete_next()
    
        # Store the workflow instance in a file.
        output = open(self.data_file, 'wb')
        pickle.dump(job, output, -1)
        output.close()
        before = job.get_dump()

        # Load the workflow instance from a file and delete the file.
        input = open(self.data_file, 'rb')
        job   = pickle.load(input)
        input.close()
        os.remove(self.data_file)
        after = job.get_dump()

        # Make sure that the state of the job did not change.
        self.assert_(before == after, 'Before:\n' + before + '\n' \
                                    + 'After:\n'  + after  + '\n')

        # Re-connect signals, because the pickle dump now only contains a 
        # copy of self.taken_path.
        for name, task in job.workflow.tasks.iteritems():
            task.signal_disconnect('reached',   on_reached_cb)
            task.signal_disconnect('completed', on_complete_cb)
            task.signal_connect('reached',
                                on_reached_cb,
                                self.taken_path['reached'])
            task.signal_connect('completed',
                                on_complete_cb,
                                self.taken_path['completed'])

        # Run the rest of the workflow.
        job.complete_all()
        after = job.get_dump()
        self.assert_(job.is_completed(), 'Job done, but not complete:' + after)
        assert_same_path(self,
                         self.expected_path,
                         self.taken_path['completed'])


    def testPickle(self):
        # Read a complete workflow.
        file = os.path.join(os.path.dirname(__file__), 'xml/spiff/workflow1.xml')

        for i in xrange(5):
            workflow_list = self.reader.parse_file(file)
            wf            = workflow_list[0]
            job           = Job(wf)
            self.testPickleSingle(wf, job)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
