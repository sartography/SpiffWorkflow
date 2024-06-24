from SpiffWorkflow import TaskState
from SpiffWorkflow.bpmn import BpmnWorkflow
from SpiffWorkflow.bpmn.util.diff import SpecDiff, WorkflowDiff

from .BpmnWorkflowTestCase import BpmnWorkflowTestCase

class CompareSpecTest(BpmnWorkflowTestCase):

    def test_tasks_added(self):
        v1_spec, v1_sp_specs = self.load_workflow_spec('diff/v1.bpmn', 'Process')
        v2_spec, v2_sp_specs = self.load_workflow_spec('diff/v2.bpmn', 'Process')
        result = SpecDiff(self.serializer, v1_spec, v2_spec)
        self.assertEqual(len(result.added), 3)
        self.assertIn(v2_spec.task_specs.get('Gateway_1618q26'), result.added)
        self.assertIn(v2_spec.task_specs.get('Activity_1ds7clb'), result.added)
        self.assertIn(v2_spec.task_specs.get('Event_0tatpgq'), result.added)

    def test_tasks_removed(self):
        v1_spec, v1_sp_specs = self.load_workflow_spec('diff/v1.bpmn', 'Process')
        v2_spec, v2_sp_specs = self.load_workflow_spec('diff/v2.bpmn', 'Process')
        result = SpecDiff(self.serializer, v2_spec, v1_spec)
        self.assertEqual(len(result.removed), 3)
        self.assertIn(v2_spec.task_specs.get('Gateway_1618q26'), result.removed)
        self.assertIn(v2_spec.task_specs.get('Activity_1ds7clb'), result.removed)
        self.assertIn(v2_spec.task_specs.get('Event_0tatpgq'), result.removed)

    def test_tasks_changed(self):
        v2_spec, v2_sp_specs = self.load_workflow_spec('diff/v2.bpmn', 'Process')
        v3_spec, v3_sp_specs = self.load_workflow_spec('diff/v3.bpmn', 'Process')
        result = SpecDiff(self.serializer, v2_spec, v3_spec)
        # The deafult output was changed and a the conditional output was converted to a subprocess
        self.assertListEqual(
            result.changed.get(v2_spec.task_specs.get('Gateway_1618q26')),
            ['outputs', 'cond_task_specs', 'default_task_spec']
        )
        # The generic task was changed to a subprocess
        self.assertListEqual(
            result.changed.get(v2_spec.task_specs.get('Activity_1ds7clb')),
            ['typename']
        )

    def test_alignment(self):
        v2_spec, v2_sp_specs = self.load_workflow_spec('diff/v2.bpmn', 'Process')
        v3_spec, v3_sp_specs = self.load_workflow_spec('diff/v3.bpmn', 'Process')
        result = SpecDiff(self.serializer, v2_spec, v3_spec)
        old_end_event = v2_spec.task_specs.get('Event_0rilo47')
        new_end_event = v3_spec.task_specs.get('Event_18osyv3')
        self.assertEqual(result.alignment[old_end_event], new_end_event)
        for old, new in result.alignment.items():
            if old is not old_end_event:
                self.assertEqual(old.name, new.name)

    def test_multiple(self):
        v4_spec, v4_sp_specs = self.load_workflow_spec('diff/v4.bpmn', 'Process')
        v5_spec, v5_sp_specs = self.load_workflow_spec('diff/v5.bpmn', 'Process')
        result = SpecDiff(self.serializer, v4_spec, v5_spec)
        self.assertEqual(len(result.removed), 4)
        self.assertEqual(len(result.changed), 4)
        self.assertIn(v4_spec.task_specs.get('Gateway_0z1qhgl'), result.removed)
        self.assertIn(v4_spec.task_specs.get('Gateway_1acqedb'), result.removed)
        self.assertIn(v4_spec.task_specs.get('Activity_1lmz1t0'), result.removed)
        self.assertIn(v4_spec.task_specs.get('Activity_11gnihu'), result.removed)
        self.assertListEqual(
            result.changed.get(v4_spec.task_specs.get('Gateway_1618q26')),
            ['outputs', 'cond_task_specs', 'default_task_spec']
        )
        self.assertListEqual(
            result.changed.get(v4_spec.task_specs.get('Gateway_0p4fq77')),
            ['inputs']
        )
        self.assertListEqual(
            result.changed.get(v4_spec.task_specs.get('Activity_1ds7clb')),
            ['typename']
        )

class CompareWorkflowTest(BpmnWorkflowTestCase):

    def test_changed(self):
        v3_spec, v3_sp_specs = self.load_workflow_spec('diff/v3.bpmn', 'Process')
        v4_spec, v4_sp_specs = self.load_workflow_spec('diff/v4.bpmn', 'Process')
        spec_diff = SpecDiff(self.serializer, v3_spec, v4_spec)
        sp_spec_diff = SpecDiff(
            self.serializer,
            v3_sp_specs['Activity_1ds7clb'],
            v4_sp_specs['Activity_1ds7clb']
        )
        workflow = BpmnWorkflow(v3_spec, v3_sp_specs)
        task = workflow.get_next_task(state=TaskState.READY, manual=False)
        while task is not None:
            task.run()
            task = workflow.get_next_task(state=TaskState.READY, manual=False)
        wf_diff = WorkflowDiff(workflow, spec_diff)
        self.assertEqual(len(wf_diff.changed), 2)
        self.assertIn(workflow.get_next_task(spec_name='Activity_0b53566'), wf_diff.changed)
        self.assertIn(workflow.get_next_task(spec_name='Gateway_1618q26'), wf_diff.changed)
        sp = workflow.get_subprocess(workflow.get_next_task(spec_name='Activity_1ds7clb'))
        sp_diff = WorkflowDiff(sp, sp_spec_diff)
        self.assertEqual(len(sp_diff.changed), 2)
        self.assertIn(workflow.get_next_task(spec_name='Activity_0uijumg'), sp_diff.changed)
        self.assertIn(workflow.get_next_task(spec_name='Event_1wlwaz1'), sp_diff.changed)

    def test_removed(self):
        v4_spec, v4_sp_specs = self.load_workflow_spec('diff/v4.bpmn', 'Process')
        v5_spec, v5_sp_specs = self.load_workflow_spec('diff/v5.bpmn', 'Process')
        spec_diff = SpecDiff(self.serializer, v4_spec, v5_spec)
        sp_spec_diff = SpecDiff(
            self.serializer,
            v4_sp_specs['Activity_1ds7clb'],
            v5_sp_specs['Activity_1ds7clb']
        )
        workflow = BpmnWorkflow(v4_spec, v4_sp_specs)
        task = workflow.get_next_task(state=TaskState.READY)
        while task is not None:
            if task.task_spec.name != 'Activity_16ggmbf':
                task.run()
            else:
                break
            task = workflow.get_next_task(state=TaskState.READY)
        wf_diff = WorkflowDiff(workflow, spec_diff)
        self.assertEqual(len(wf_diff.removed), 5)
        self.assertIn(workflow.get_next_task(spec_name='Gateway_0z1qhgl'), wf_diff.removed)
        self.assertIn(workflow.get_next_task(spec_name='Activity_1lmz1t0'), wf_diff.removed)
        self.assertIn(workflow.get_next_task(spec_name='Activity_11gnihu'), wf_diff.removed)
        self.assertIn(workflow.get_next_task(spec_name='Gateway_1acqedb'), wf_diff.removed)

