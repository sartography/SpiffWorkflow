from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

class AdHocSubprocessTest(BpmnWorkflowTestCase):

    def setUp(self):
        spec, subprocesses = self.load_workflow_spec('ad_hoc_subprocess.bpmn', 'main')
        self.workflow = BpmnWorkflow(spec, subprocesses)

    def testAdHocSubprocess(self):
        self.actual_test()

    def testAdHocSubprocessSaveRestore(self):
        self.actual_test(True)

    def actual_test(self, save_restore=False):
        self.workflow.task_tree.data = {
            'text': '',
            'edit_requested': False,
            'revision_requested': False,
            'graphics_needed': [],
            'graphics': [],
            'editing_done': False,
            'done': False,
        }
        self.workflow.get_next_task(spec_name='Start').run()
        self.workflow.get_next_task(spec_name='StartEvent_1').run()

        # This is the only task without a condition
        ready_tasks = self.workflow.get_tasks(state=TaskState.READY)
        self.assertEqual(len(ready_tasks), 1)
        self.assertEqual(ready_tasks[0].task_spec.name, 'research')
        ready_tasks[0].data['graphics_needed'] = ['fig 1', 'fig 2']
        ready_tasks[0].run()

        # I can't use the base method here because it breaks with the delta serializer
        # Frankly, I'm amazed that all the other tests pass, as the root cause seems to be
        # based on the order in which values are retrieved from the task data.
        # The workflow will complete after deserialization, so that's going to have to
        # suffice.
        if save_restore:
            dct = self.serializer.to_dict(self.workflow)
            self.workflow = self.serializer.from_dict(dct)

        first_draft = self.workflow.get_next_task(spec_name='first_draft', state=TaskState.READY)
        first_draft.data['text'] = 'first draft'
        first_draft.data['edit_requested'] = True
        first_draft.run()

        organize_refs = self.workflow.get_next_task(spec_name='organize_references', state=TaskState.READY)
        organize_refs.run()

        # At this point, graphics and editing are needed
        self.assertEqual(len(self.workflow.get_tasks(state=TaskState.READY)), 2)

        edit = self.workflow.get_next_task(spec_name='edit', state=TaskState.READY)
        edit.data['revisions'] = ['rev 1', 'rev 2']
        edit.data['revision_requested'] = True
        edit.data['edit_requested'] = False
        edit.run()

        make_graphics = self.workflow.get_next_task(spec_name='make_graphics', state=TaskState.READY)

        # Now revise whould be active instead of edit
        self.assertEqual(len(self.workflow.get_tasks(state=TaskState.READY)), 2)

        # This should reactivate edit
        make_graphics.data['graphics'] = list(make_graphics.data['graphics_needed'])
        make_graphics.data['edit_requested'] = True
        make_graphics.run()

        self.assertEqual(len(self.workflow.get_tasks(state=TaskState.READY)), 2)

        revise = self.workflow.get_next_task(spec_name='revise', state=TaskState.READY)
        revise.data['text'] = 'second draft'
        revise.data['edit_requested'] = True
        revise.data['revision_requested'] = False
        # Irrelevant variables will need to be removed so they don't overwrite updated ones
        # This should be done for all the tasks, but I don't have the patience for that
        # People will need to be *really* careful using this type of task spec
        revise.data.pop('graphics', None)
        revise.data.pop('graphics_needed', None)
        revise.run()

        # Only edit should be ready
        self.assertEqual(len(self.workflow.get_tasks(state=TaskState.READY)), 1)
        edit = self.workflow.get_next_task(spec_name='edit', state=TaskState.READY)
        edit.data['graphics_needed'].append('fig 3')
        edit.data['revisions'] = ['rev 3']
        edit.data['revision_requested'] = True
        edit.data['edit_requested'] = False
        edit.run()

        # Graphics and revise should be active now
        self.assertEqual(len(self.workflow.get_tasks(state=TaskState.READY)), 2)

        revise = self.workflow.get_next_task(spec_name='revise', state=TaskState.READY)
        revise.data['text'] = 'third draft'
        revise.data['edit_requested'] = True
        revise.data['revision_requested'] = False
        revise.run()

        # Graphics and edit should be active now
        self.assertEqual(len(self.workflow.get_tasks(state=TaskState.READY)), 2)
        edit = self.workflow.get_next_task(spec_name='edit', state=TaskState.READY)
        edit.data['edit_requested'] = False
        edit.run()

        make_graphics = self.workflow.get_next_task(spec_name='make_graphics', state=TaskState.READY)
        make_graphics.data['graphics'] = list(make_graphics.data['graphics_needed'])
        make_graphics.data['edit_requested'] = True
        make_graphics.data.pop('text', None)
        make_graphics.data.pop('revision_requested', None)
        make_graphics.run()

        # Final edit
        self.assertEqual(len(self.workflow.get_tasks(state=TaskState.READY)), 1)
        edit = self.workflow.get_next_task(spec_name='edit', state=TaskState.READY)
        edit.data['edit_requested'] = False
        edit.data['editing_done'] = True
        edit.run()

        gateway = self.workflow.get_next_task(spec_name='Gateway_1bp40us', state=TaskState.READY)
        gateway.run()

        finalize = self.workflow.get_next_task(spec_name='finalize', state=TaskState.READY)
        finalize.data['done'] = True
        finalize.run()

        self.workflow.do_engine_steps()
        self.assertTrue(self.workflow.completed)
        self.assertEqual(self.workflow.data['text'], 'third draft')
        self.assertEqual(len(self.workflow.data['graphics']), 3)
