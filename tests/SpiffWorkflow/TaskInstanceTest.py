import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

def suite():
    tests = ['testTree']
    return unittest.TestSuite(map(TaskInstanceTest, tests))

from SpiffWorkflow           import Workflow, TaskInstance
from SpiffWorkflow.Tasks     import Task
from SpiffWorkflow.Exception import WorkflowException

class TaskInstanceTest(unittest.TestCase):
    def setUp(self):
        pass


    def testTree(self):
        # Build a tree.
        wf       = Workflow()
        task1    = Task(wf, 'Task 1')
        task2    = Task(wf, 'Task 2')
        task3    = Task(wf, 'Task 3')
        task4    = Task(wf, 'Task 4')
        task5    = Task(wf, 'Task 5')
        task6    = Task(wf, 'Task 6')
        task7    = Task(wf, 'Task 7')
        task8    = Task(wf, 'Task 8')
        task9    = Task(wf, 'Task 9')
        root     = TaskInstance(object, task1)
        c1       = root._add_child(task2)
        c11      = c1._add_child(task3)
        c111     = c11._add_child(task4)
        c1111    = TaskInstance(object, task5, c111)
        c112     = TaskInstance(object, task6, c11)
        c12      = TaskInstance(object, task7, c1)
        c2       = TaskInstance(object, task8, root)
        c3       = TaskInstance(object, task9, root)
        c3.state = TaskInstance.COMPLETED

        # Check whether the tree is built properly.
        expected = """1/0: TaskInstance of Task 1 State: FUTURE Children: 3
  2/0: TaskInstance of Task 2 State: FUTURE Children: 2
    3/0: TaskInstance of Task 3 State: FUTURE Children: 2
      4/0: TaskInstance of Task 4 State: FUTURE Children: 1
        5/0: TaskInstance of Task 5 State: FUTURE Children: 0
      6/0: TaskInstance of Task 6 State: FUTURE Children: 0
    7/0: TaskInstance of Task 7 State: FUTURE Children: 0
  8/0: TaskInstance of Task 8 State: FUTURE Children: 0
  9/0: TaskInstance of Task 9 State: COMPLETED Children: 0"""
        self.assert_(expected == root.get_dump(),
                     'Expected:\n' + repr(expected) + '\n' + \
                     'but got:\n'  + repr(root.get_dump()))

        # Now remove one line from the expected output for testing the
        # filtered iterator.
        expected2 = ''
        for line in expected.split('\n'):
            if line.find('Task 9') >= 0:
                continue
            expected2 += line.lstrip() + '\n'

        # Run the iterator test.
        result = ''
        for node in TaskInstance.Iterator(root, TaskInstance.FUTURE):
            result += node.get_dump(0, False) + '\n'
        self.assert_(expected2 == result,
                     'Expected:\n' + expected2 + '\n' + \
                     'but got:\n'  + result)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
