import sys, unittest, re, os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from SpiffWorkflow import Workflow
from SpiffWorkflow.specs import *
from SpiffWorkflow.operators import *
from SpiffWorkflow.Task import *
from SpiffWorkflow.specs.Simple import Simple

def append_step(path, task, signal_name):
    path.append((task._get_depth(), task.get_name()))
    #print task._get_depth(), '.', signal_name, task.get_name(), len(path)


def on_reached_cb(workflow, task, taken_path):
    append_step(taken_path, task, 'reached')
    reached_key = '%s_reached' % task.get_name()
    n_reached   = task.get_attribute(reached_key, 0) + 1
    step        = task.get_attribute('step', 1) + 1
    task.set_attribute(**{reached_key: n_reached})
    task.set_attribute(two             = 2)
    task.set_attribute(three           = 3)
    task.set_attribute(step            = step)
    task.set_attribute(test_attribute1 = 'false')
    task.set_attribute(test_attribute2 = 'true')


def on_complete_cb(workflow, task, taken_path):
    append_step(taken_path, task, 'completed')
    return True


def format_path(path):
    '''
    Format a path for printing.
    
    path -- list containing tuples.
    '''
    string = ''
    for i, (depth, name) in enumerate(path):
        string += '%2s.%sBranch %s: %s\n' % (i + 1, ' '*depth, depth, name)
    return string


def assert_same_path(test, expected_path, taken_path):
    expected = format_path(expected_path)
    taken    = format_path(taken_path)
    error    = 'Expected:\n'
    error   += '%s\n'        % expected
    error   += 'but got:\n'
    error   += '%s\n'        % taken

    # Check whether the correct route was taken.
    for i, (depth, name) in enumerate(expected_path):
        test.assert_(i < len(taken_path), error)
        msg = 'At step %s:' % (i + 1)
        test.assert_(name == taken_path[i][1], msg + '\n' + error)

    test.assert_(expected == taken, error)


class WorkflowTest(unittest.TestCase):
    '''
    WARNING: Make sure to keep this test in sync with XmlReaderTest! Any
    change will break both tests!
    '''
    def setUp(self):
        self.expected_path = \
                 [( 1, 'Start'),
                  ( 2, 'task_a1'),
                  ( 3, 'task_a2'),
                  ( 2, 'task_b1'),
                  ( 3, 'task_b2'),
                  ( 4, 'synch_1'),
                  ( 5, 'excl_choice_1'),
                  ( 6, 'task_c1'),
                  ( 7, 'excl_choice_2'),
                  ( 8, 'task_d3'),
                  ( 9, 'multi_choice_1'),
                  (10, 'task_e1'),
                  (10, 'task_e3'),
                  (11, 'struct_synch_merge_1'),
                  (12, 'task_f1'),
                  (13, 'struct_discriminator_1'),
                  (14, 'excl_choice_3'),
                  (15, 'excl_choice_1'),
                  (16, 'task_c1'),
                  (17, 'excl_choice_2'),
                  (18, 'task_d3'),
                  (19, 'multi_choice_1'),
                  (20, 'task_e1'),
                  (20, 'task_e3'),
                  (21, 'struct_synch_merge_1'),
                  (22, 'task_f1'),
                  (23, 'struct_discriminator_1'),
                  (24, 'excl_choice_3'),
                  (25, 'multi_instance_1'),
                  (26, 'task_g1'),
                  (26, 'task_g2'),
                  (26, 'task_g1'),
                  (26, 'task_g2'),
                  (26, 'task_g1'),
                  (26, 'task_g2'),
                  (27, 'struct_synch_merge_2'),
                  (28, 'last'),
                  (29, 'End'),
                  (22, 'task_f2'),
                  (22, 'task_f3'),
                  (12, 'task_f2'),
                  (12, 'task_f3')]

    def _createWorkflowSpec(self):
        wf_spec = WorkflowSpec()
        # Build one branch.
        a1 = Simple(wf_spec, 'task_a1')
        wf_spec.start.connect(a1)

        a2 = Simple(wf_spec, 'task_a2')
        a1.connect(a2)

        # Build another branch.
        b1 = Simple(wf_spec, 'task_b1')
        wf_spec.start.connect(b1)

        b2 = Simple(wf_spec, 'task_b2')
        b1.connect(b2)

        # Merge both branches (synchronized).
        synch_1 = Join(wf_spec, 'synch_1')
        a2.connect(synch_1)
        b2.connect(synch_1)

        # If-condition that does not match.
        excl_choice_1 = ExclusiveChoice(wf_spec, 'excl_choice_1')
        synch_1.connect(excl_choice_1)

        c1 = Simple(wf_spec, 'task_c1')
        excl_choice_1.connect(c1)

        c2 = Simple(wf_spec, 'task_c2')
        cond = Equal(Attrib('test_attribute1'), Attrib('test_attribute2'))
        excl_choice_1.connect_if(cond, c2)

        c3 = Simple(wf_spec, 'task_c3')
        excl_choice_1.connect_if(cond, c3)

        # If-condition that matches.
        excl_choice_2 = ExclusiveChoice(wf_spec, 'excl_choice_2')
        c1.connect(excl_choice_2)
        c2.connect(excl_choice_2)
        c3.connect(excl_choice_2)

        d1 = Simple(wf_spec, 'task_d1')
        excl_choice_2.connect(d1)

        d2 = Simple(wf_spec, 'task_d2')
        excl_choice_2.connect_if(cond, d2)

        d3 = Simple(wf_spec, 'task_d3')
        cond = Equal(Attrib('test_attribute1'), Attrib('test_attribute1'))
        excl_choice_2.connect_if(cond, d3)

        # If-condition that does not match.
        multichoice = MultiChoice(wf_spec, 'multi_choice_1')
        d1.connect(multichoice)
        d2.connect(multichoice)
        d3.connect(multichoice)

        e1 = Simple(wf_spec, 'task_e1')
        multichoice.connect_if(cond, e1)

        e2 = Simple(wf_spec, 'task_e2')
        cond = Equal(Attrib('test_attribute1'), Attrib('test_attribute2'))
        multichoice.connect_if(cond, e2)

        e3 = Simple(wf_spec, 'task_e3')
        cond = Equal(Attrib('test_attribute2'), Attrib('test_attribute2'))
        multichoice.connect_if(cond, e3)

        # StructuredSynchronizingMerge
        syncmerge = Join(wf_spec, 'struct_synch_merge_1', 'multi_choice_1')
        e1.connect(syncmerge)
        e2.connect(syncmerge)
        e3.connect(syncmerge)

        # Implicit parallel split.
        f1 = Simple(wf_spec, 'task_f1')
        syncmerge.connect(f1)

        f2 = Simple(wf_spec, 'task_f2')
        syncmerge.connect(f2)

        f3 = Simple(wf_spec, 'task_f3')
        syncmerge.connect(f3)

        # Discriminator
        discrim_1 = Join(wf_spec,
                         'struct_discriminator_1',
                         'struct_synch_merge_1',
                         threshold = 1)
        f1.connect(discrim_1)
        f2.connect(discrim_1)
        f3.connect(discrim_1)

        # Loop back to the first exclusive choice.
        excl_choice_3 = ExclusiveChoice(wf_spec, 'excl_choice_3')
        discrim_1.connect(excl_choice_3)
        cond = NotEqual(Attrib('excl_choice_3_reached'), Attrib('two'))
        excl_choice_3.connect_if(cond, excl_choice_1)

        # Split into 3 branches, and implicitly split twice in addition.
        multi_instance_1 = MultiInstance(wf_spec, 'multi_instance_1', times = 3)
        excl_choice_3.connect(multi_instance_1)

        # Parallel tasks.
        g1 = Simple(wf_spec, 'task_g1')
        g2 = Simple(wf_spec, 'task_g2')
        multi_instance_1.connect(g1)
        multi_instance_1.connect(g2)

        # StructuredSynchronizingMerge
        syncmerge2 = Join(wf_spec, 'struct_synch_merge_2', 'multi_instance_1')
        g1.connect(syncmerge2)
        g2.connect(syncmerge2)

        # Add a final task.
        last = Simple(wf_spec, 'last')
        syncmerge2.connect(last)

        # Add another final task :-).
        end = Simple(wf_spec, 'End')
        last.connect(end)
        return wf_spec

    def testCompleteWorkflowAutomatically(self):
        wf_spec = self._createWorkflowSpec()
        self._runWorkflow(wf_spec)

    def _runWorkflow(self, wf_spec):
        taken_path = {'reached':   [],
                      'completed': []}
        for name, task in wf_spec.task_specs.iteritems():
            task.reached_event.connect(on_reached_cb, taken_path['reached'])
            task.completed_event.connect(on_complete_cb, taken_path['completed'])

        # Execute all tasks within the Workflow.
        workflow = Workflow(wf_spec)
        self.assert_(not workflow.is_completed(), 'Workflow complete before start')
        try:
            workflow.complete_all()
        except:
            workflow.dump()
            raise

        self.assert_(workflow.is_completed(),
                     'complete_all() returned, but workflow is not complete\n'
                   + workflow.task_tree.get_dump())
        #workflow.task_tree.dump()

        assert_same_path(self, self.expected_path, taken_path['completed'])

    def testBeginWorkflowStepByStep(self):
        """
            Simulates interactive calls, as would be issued by a user.
            """
        wf_spec = self._createWorkflowSpec()
        workflow = Workflow(wf_spec)

        tasks = workflow.get_tasks(Task.READY)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_spec.name, 'Start')
        workflow.complete_task_from_id(tasks[0].id)
        self.assertEqual(tasks[0].state, Task.COMPLETED)

        tasks = workflow.get_tasks(Task.READY)
        self.assertEqual(len(tasks), 2)
        task_a1 = tasks[0]
        task_b1 = tasks[1]
        self.assertEqual(task_a1.task_spec.__class__, Simple)
        self.assertEqual(task_a1.task_spec.name, 'task_a1')
        self.assertEqual(task_b1.task_spec.__class__, Simple)
        self.assertEqual(task_b1.task_spec.name, 'task_b1')
        workflow.complete_task_from_id(task_a1.id)
        self.assertEqual(task_a1.state, Task.COMPLETED)

        tasks = workflow.get_tasks(Task.READY)
        self.assertEqual(len(tasks), 2)
        self.assertTrue(task_b1 in tasks)
        task_a2 = tasks[0]
        self.assertEqual(task_a2.task_spec.__class__, Simple)
        self.assertEqual(task_a2.task_spec.name, 'task_a2')
        workflow.complete_task_from_id(task_a2.id)

        tasks = workflow.get_tasks(Task.READY)
        self.assertEqual(len(tasks), 1)
        self.assertTrue(task_b1 in tasks)

        workflow.complete_task_from_id(task_b1.id)
        tasks = workflow.get_tasks(Task.READY)
        self.assertEqual(len(tasks), 1)
        workflow.complete_task_from_id(tasks[0].id)

        tasks = workflow.get_tasks(Task.READY)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_spec.name, 'synch_1')
        # haven't reached the end of the workflow, but stopping at "synch_1"



def suite():
    return unittest.TestLoader().loadTestsFromTestCase(WorkflowTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())
