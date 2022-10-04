# -*- coding: utf-8 -*-

import sys
import unittest
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from SpiffWorkflow.workflow import Workflow
from SpiffWorkflow.specs import Join, MultiChoice, WorkflowSpec
from SpiffWorkflow.operators import Attrib, Equal, PathAttrib
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.specs.Simple import Simple
from SpiffWorkflow.serializer.dict import DictionarySerializer


class ASmallWorkflow(WorkflowSpec):

    def __init__(self):
        super(ASmallWorkflow, self).__init__(name="asmallworkflow")

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

        tasks = workflow.get_tasks(TaskState.READY)
        task_start = tasks[0]
        workflow.complete_task_from_id(task_start.id)

        tasks = workflow.get_tasks(TaskState.READY)
        multichoice = tasks[0]
        workflow.complete_task_from_id(multichoice.id)

        tasks = workflow.get_tasks(TaskState.READY)
        task_a1 = tasks[0]
        workflow.complete_task_from_id(task_a1.id)
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
        self.assertEqual(
            1, len([t for t in new_workflow.get_tasks() if t.task_spec.name == 'Start']))
        self.assertEqual(
            1, len([t for t in new_workflow.get_tasks() if t.task_spec.name == 'Root']))

    def testDeserialization(self):
        """
        Tests the that deserialized workflow can be completed.
        """
        old_workflow = self.workflow

        old_workflow.complete_next()
        self.assertEqual('task_a2', old_workflow.last_task.get_name())
        serializer = DictionarySerializer()
        serialized_workflow = old_workflow.serialize(serializer)

        serializer = DictionarySerializer()
        new_workflow = Workflow.deserialize(serializer, serialized_workflow)
        self.assertEqual('task_a2', old_workflow.last_task.get_name())
        new_workflow.complete_all()
        self.assertEqual('task_a2', old_workflow.last_task.get_name())


def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PersistSmallWorkflowTest)
if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
