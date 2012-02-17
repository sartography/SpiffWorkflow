import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from SpiffWorkflow           import Workflow, Task
from SpiffWorkflow.Job       import TaskIdAssigner
from SpiffWorkflow.specs     import Simple
from SpiffWorkflow.Exception import WorkflowException

class MockJob(object):
    def __init__(self):
        self.task_id_assigner = TaskIdAssigner()

class TaskTest(unittest.TestCase):
    def setUp(self):
        Task.id_pool = 0
        Task.thread_id_pool = 0

    def testTree(self):
        # Build a tree.
        wf       = Workflow()
        job      = MockJob()
        task1    = Simple(wf, 'Simple 1')
        task2    = Simple(wf, 'Simple 2')
        task3    = Simple(wf, 'Simple 3')
        task4    = Simple(wf, 'Simple 4')
        task5    = Simple(wf, 'Simple 5')
        task6    = Simple(wf, 'Simple 6')
        task7    = Simple(wf, 'Simple 7')
        task8    = Simple(wf, 'Simple 8')
        task9    = Simple(wf, 'Simple 9')
        root     = Task(job, task1)
        c1       = root._add_child(task2)
        c11      = c1._add_child(task3)
        c111     = c11._add_child(task4)
        c1111    = Task(job, task5, c111)
        c112     = Task(job, task6, c11)
        c12      = Task(job, task7, c1)
        c2       = Task(job, task8, root)
        c3       = Task(job, task9, root)
        c3.state = Task.COMPLETED

        # Check whether the tree is built properly.
        expected = """1/0: Task of Simple 1 State: FUTURE Children: 3
  2/0: Task of Simple 2 State: FUTURE Children: 2
    3/0: Task of Simple 3 State: FUTURE Children: 2
      4/0: Task of Simple 4 State: FUTURE Children: 1
        5/0: Task of Simple 5 State: FUTURE Children: 0
      6/0: Task of Simple 6 State: FUTURE Children: 0
    7/0: Task of Simple 7 State: FUTURE Children: 0
  8/0: Task of Simple 8 State: FUTURE Children: 0
  9/0: Task of Simple 9 State: COMPLETED Children: 0"""
        self.assert_(expected == root.get_dump(),
                     'Expected:\n' + repr(expected) + '\n' + \
                     'but got:\n'  + repr(root.get_dump()))

        # Now remove one line from the expected output for testing the
        # filtered iterator.
        expected2 = ''
        for line in expected.split('\n'):
            if line.find('Simple 9') >= 0:
                continue
            expected2 += line.lstrip() + '\n'

        # Run the iterator test.
        result = ''
        for thetask in Task.Iterator(root, Task.FUTURE):
            result += thetask.get_dump(0, False) + '\n'
        self.assert_(expected2 == result,
                     'Expected:\n' + expected2 + '\n' + \
                     'but got:\n'  + result)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(TaskTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
