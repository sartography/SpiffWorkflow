import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

def suite():
    tests = ['testTaskInfo']
    return unittest.TestSuite(map(TaskInfoTest, tests))

from SpiffWorkflow.Server import TaskInfo

class TaskInfoTest(unittest.TestCase):
    def testTaskInfo(self):
        info = TaskInfo()

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
