import json
import unittest
from SpiffWorkflow.Task import Task
from SpiffWorkflow.Workflow import TaskIdAssigner, Workflow
from SpiffWorkflow.operators import Equal, Attrib, Assign
from SpiffWorkflow.specs.ExclusiveChoice import ExclusiveChoice
from SpiffWorkflow.specs.Join import Join
from SpiffWorkflow.specs.Simple import Simple
from SpiffWorkflow.specs.StartTask import StartTask
from SpiffWorkflow.specs.WorkflowSpec import WorkflowSpec
from SpiffWorkflow.storage.DictionarySerializer import DictionarySerializer
from SpiffWorkflow.storage.JSONSerializer import JSONSerializer

__author__ = 'matth'


class WorkflowTest(unittest.TestCase):

    def restore_ready_task(self, target_task):
        matches = sorted([t for t in self.workflow.get_tasks()  if t.task_spec.name == target_task], key=lambda t: t.id)
        self.assertGreater(len(matches), 0)
        task = matches[0]
        if task.state != Task.READY:
            self.complete_task(task.parent, task)
        assert task.state == Task.READY

    def complete_task(self, task, target_child):
        if task.state != Task.READY:
            self.complete_task(task.parent, task)
        assert task.state == Task.READY
        task._set_state(Task.COMPLETED | (task.state & Task.TRIGGERED))
        task._update_children(target_child.task_spec)


    def do_next_exclusive_step(self, step_name, with_save_load=False, set_attribs=None):
        if with_save_load:
            self._do_save_and_load()

        tasks = self.workflow.get_tasks(Task.READY)
        self._do_single_step(step_name, tasks, set_attribs)

    def do_next_named_step(self, step_name, with_save_load=False, set_attribs=None):
        if with_save_load:
            self._do_save_and_load()

        tasks = filter(lambda t: t.task_spec.name == step_name, self.workflow.get_tasks(Task.READY))

        self._do_single_step(step_name, tasks, set_attribs)

    def _do_single_step(self, step_name, tasks, set_attribs=None):

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_spec.name, step_name)
        if set_attribs:
            tasks[0].set_attribute(**set_attribs)
        self.workflow.complete_task_from_id(tasks[0].id)

    def _do_save_and_load(self):
        state = self.workflow.serialize(JSONSerializer())
        new_workflow = JSONSerializer().deserialize_workflow(state)
        new_state = new_workflow.serialize(JSONSerializer())
        pretty_state = json.dumps(json.loads(state), sort_keys=True, indent=4)
        pretty_new_state = json.dumps(json.loads(new_state), sort_keys=True, indent=4)
        self.assertEqual(pretty_state, pretty_new_state)
        self.assertEquals(len(self.workflow.get_tasks(Task.READY)), len(new_workflow.get_tasks(Task.READY)))
        self.assertEquals(self.workflow.get_tasks(Task.READY)[0].id, new_workflow.get_tasks(Task.READY)[0].id)
        self.assertEquals(self.workflow.get_tasks(Task.READY)[0].task_spec.name, new_workflow.get_tasks(Task.READY)[0].task_spec.name)
        self.workflow = new_workflow

class MocStage1Test(WorkflowTest):
    def setUp(self):
        self.spec = self.build_moc_stage1_spec()

    def build_moc_stage1_spec(self):
        spec     = WorkflowSpec()
        task1    = Simple(spec, 'prepare-moc-proposal', description='Prepare MOC Proposal')
        task1.follow(spec.start)
        task2    = Simple(spec, 'dgm-review', desciption='Review')
        task2.follow(task1)
        excl_choice_1 = ExclusiveChoice(spec, 'dgm-review-result')
        excl_choice_1.follow(task2)
        task3    = Simple(spec, 'record-on-agenda', desciption='Record on MOC agenda')
        approve_cond = Equal(Attrib('status'), 'Approve')
        send_back_cond = Equal(Attrib('status'), 'Send Back (Insufficient Details)')
        cancel_cond = Equal(Attrib('status'), 'Cancel')
        excl_choice_1.connect_if(send_back_cond, task1)
        excl_choice_1.connect_if(cancel_cond, task1)
        excl_choice_1.connect_if(approve_cond, task3)
        # We have to have a default:
        excl_choice_1.connect(task1)

        return spec

    def testMocStage1RunThrough(self):

        self.workflow = Workflow(self.spec)

        self.do_next_exclusive_step('Start')
        self.do_next_exclusive_step('prepare-moc-proposal')
        self.do_next_exclusive_step('dgm-review', set_attribs={'status':'Approve'})
        self.do_next_exclusive_step('dgm-review-result')
        self.do_next_exclusive_step('record-on-agenda')

    def testMocStage1RunThroughCancel(self):

        self.workflow = Workflow(self.spec)

        self.do_next_exclusive_step('Start')
        self.do_next_exclusive_step('prepare-moc-proposal')
        self.do_next_exclusive_step('dgm-review', set_attribs={'status':'Cancel'})
        self.do_next_exclusive_step('dgm-review-result')
        self.do_next_exclusive_step('prepare-moc-proposal')
        self.do_next_exclusive_step('dgm-review', set_attribs={'status':'Approve'})
        self.do_next_exclusive_step('dgm-review-result')
        self.do_next_exclusive_step('record-on-agenda')

    def testMocStage1RunThroughSendBack(self):

        self.workflow = Workflow(self.spec)

        self.do_next_exclusive_step('Start')

        for i in range(0,10):
            self.do_next_exclusive_step('prepare-moc-proposal',with_save_load=False)
            self.do_next_exclusive_step('dgm-review', set_attribs={'status':'Send Back (Insufficient Details)'},with_save_load=False)
            self.do_next_exclusive_step('dgm-review-result',with_save_load=False)

        self.do_next_exclusive_step('prepare-moc-proposal',with_save_load=False)
        self.do_next_exclusive_step('dgm-review', set_attribs={'status':'Send Back (Insufficient Details)'},with_save_load=False)
        self.do_next_exclusive_step('dgm-review-result',with_save_load=False)
        self._do_save_and_load()

        self.do_next_exclusive_step('prepare-moc-proposal')
        self.do_next_exclusive_step('dgm-review', set_attribs={'status':'Approve'})
        self.do_next_exclusive_step('dgm-review-result')
        self.do_next_exclusive_step('record-on-agenda')


    def test_simple_save_load(self):
        self.workflow = Workflow(self.spec)

        self.do_next_exclusive_step('Start')
        self.do_next_exclusive_step('prepare-moc-proposal')

        state = self.workflow.serialize(JSONSerializer())

        old_workflow = self.workflow
        self.workflow = JSONSerializer().deserialize_workflow(state)
        new_state = self.workflow.serialize(JSONSerializer())
        self.assertEqual(json.dumps(json.loads(state), sort_keys=True), json.dumps(json.loads(new_state), sort_keys=True))

        tasks = self.workflow.get_tasks(Task.READY)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_spec.name, 'dgm-review')

        old_tasks = old_workflow.get_tasks(Task.READY)
        self.assertEqual(len(old_tasks), 1)
        self.assertEqual(old_tasks[0].task_spec.name, 'dgm-review')

        tasks[0].set_attribute(**{'status':'Approve'})
        old_tasks[0].set_attribute(**{'status':'Approve'})

        old_workflow.complete_task_from_id(old_tasks[0].id)
        self.workflow.complete_task_from_id(tasks[0].id)

        self.do_next_exclusive_step('dgm-review-result')
        self.do_next_exclusive_step('record-on-agenda')

    def test_restore_ready_task(self):
        self.workflow = Workflow(self.spec)

        self.restore_ready_task('dgm-review')

        self.do_next_exclusive_step('dgm-review', set_attribs={'status':'Approve'})
        self.do_next_exclusive_step('dgm-review-result')
        self.do_next_exclusive_step('record-on-agenda')

    def test_restore_ready_task_after_branch(self):
        self.workflow = Workflow(self.spec)

        self.restore_ready_task('record-on-agenda')
        self.do_next_exclusive_step('record-on-agenda')


class HandoverTest(WorkflowTest):
    def setUp(self):
        self.spec = self.build_handover_spec()

    def build_handover_spec(self):
        spec     = WorkflowSpec()
        task1    = Simple(spec, 'open-for-approval', description='Set Open for Approval')
        task1.follow(spec.start)

        #path 1:
        p1_task1    = Simple(spec, 'outgoing-operator-approval', desciption='Outgoing Operator Approval')
        p1_task1.follow(task1)

        p1_task2    = Simple(spec, 'supervisor-approval', desciption='Supervisor Approval')
        p1_task2.follow(p1_task1)

        p1_task3    = Simple(spec, 'create-new-handover', desciption='Create New Handover')
        p1_task3.follow(p1_task2)

        #path 2
        p2_task1    = Simple(spec, 'gm-approval', desciption='GM Approval')
        p2_task1.follow(task1)

        # join
        join1 = Join(spec, 'join1')
        join1.follow(p1_task3)
        join1.follow(p2_task1)

        end_task    = Simple(spec, 'shift-report', description='Send Shift Report')
        end_task.follow(join1)

        return spec


    def test_run_through(self):

        self.workflow = Workflow(self.spec)

        self.do_next_exclusive_step('Start')
        self.do_next_exclusive_step('open-for-approval')

        #path 1:
        self.do_next_named_step('outgoing-operator-approval')
        self.do_next_named_step('supervisor-approval')
        self.do_next_named_step('create-new-handover')

        #path 2
        self.do_next_named_step('gm-approval')

        self.do_next_exclusive_step('join1')
        self.do_next_exclusive_step('shift-report')


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MocStage1Test)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity = 2).run(suite())