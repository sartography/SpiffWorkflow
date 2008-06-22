import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

def suite():
    tests = ['testJobInfo']
    return unittest.TestSuite(map(JobInfoTest, tests))

from SpiffWorkflow.Server import JobInfo

class JobInfoTest(unittest.TestCase):
    def testJobInfo(self):
        info = JobInfo()

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
