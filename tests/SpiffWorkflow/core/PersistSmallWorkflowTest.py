import unittest

from SpiffWorkflow import TaskState, Workflow
from SpiffWorkflow.specs import Join, MultiChoice, WorkflowSpec, Simple
from SpiffWorkflow.operators import Attrib, Equal, PathAttrib
from SpiffWorkflow.serializer.dict import DictionarySerializer


class ASmallWorkflow(WorkflowSpec):

    def __init__(self):
        super(ASmallWorkflow, self).__init__(name="asmallworkflow", addstart=True)

        multichoice = MultiChoice(self, 'multi_choice_1')
        self.start.connect(multichoice)

        a1 = Simple(self, 'task_a1')
        multichoice.connect(a1)

        a2 = Simple(self, 'task_a2')
        cond = Equal(Attrib('test_attribute1'), PathAttrib('test/attribute2'))
        multichoice.connect_if(cond, a2)

        syncmerge = Join(self, 'struct_synch_merge_1', 'multi_choice_1')
        a1.connect(syncmerge)
        a2.connect(syncmerge)

        end = Simple(self, 'End')
        syncmerge.connect(end)


class PersistSmallWorkflowTest(unittest.TestCase):

    """Runs persistency tests agains a small and easy to inspect workflowdefinition"""

    def setUp(self):
        self.wf_spec = ASmallWorkflow()
        self.workflow = self._advance_to_a1(self.wf_spec)

    def _advance_to_a1(self, wf_spec):
        workflow = Workflow(wf_spec)

        tasks = workflow.get_tasks(state=TaskState.READY)
        task_start = tasks[0]
        workflow.run_task_from_id(task_start.id)

        tasks = workflow.get_tasks(state=TaskState.READY)
        multichoice = tasks[0]
        workflow.run_task_from_id(multichoice.id)

        tasks = workflow.get_tasks(state=TaskState.READY)
        task_a1 = tasks[0]
        workflow.run_task_from_id(task_a1.id)
        return workflow

    def testDictionarySerializer(self):
        """
        Tests the SelectivePickler serializer for persisting Workflows and Tasks.
        """
        old_workflow = self.workflow
        serializer = DictionarySerializer()
        serialized_workflow = old_workflow.serialize(serializer)

        serializer = DictionarySerializer()
        new_workflow = Workflow.deserialize(serializer, serialized_workflow)

        before = old_workflow.get_dump()
        after = new_workflow.get_dump()
        self.assertEqual(before, after)

    def testDeserialization(self):
        """
        Tests the that deserialized workflow matches the original workflow
        """
        old_workflow = self.workflow
        old_workflow.spec.start.set_data(marker=True)
        serializer = DictionarySerializer()
        serialized_workflow = old_workflow.serialize(serializer)

        serializer = DictionarySerializer()
        new_workflow = Workflow.deserialize(serializer, serialized_workflow)

        self.assertEqual(
            len(new_workflow.get_tasks()), len(old_workflow.get_tasks()))
        self.assertEqual(new_workflow.spec.start.get_data(
            'marker'), old_workflow.spec.start.get_data('marker'))
        self.assertEqual(1, len([t for t in new_workflow.get_tasks() if t.task_spec.name == 'Start']))

    def testCompleteAfterDeserialization(self):
        """
        Tests the that deserialized workflow can be completed.
        """
        old_workflow = self.workflow

        old_workflow.run_next()
        self.assertEqual('task_a2', old_workflow.last_task.task_spec.name)
        serializer = DictionarySerializer()
        serialized_workflow = old_workflow.serialize(serializer)

        serializer = DictionarySerializer()
        new_workflow = Workflow.deserialize(serializer, serialized_workflow)
        self.assertEqual('task_a2', old_workflow.last_task.task_spec.name)
        new_workflow.run_all()
        self.assertEqual('task_a2', old_workflow.last_task.task_spec.name)
