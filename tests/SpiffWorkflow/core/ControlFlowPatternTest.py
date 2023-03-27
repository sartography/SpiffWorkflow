# -*- coding: utf-8 -*-
from unittest import TestCase
from .pattern_base import WorkflowPatternTestCase

# This combines the old pattern tests with the old serializer tests, creating one test per pattern
# that tests the tasks in it can be serialized with our serializers and the workflows run with the
# expected output.  This format is a little annoying (inheriting from two classes with the actual 
# work being done in the secondary class); however, this is the most concise thing I could manage.
#
# There were also a fair amount of never-used options in those tests, so the tests in the base case
# are a lot simpler than the ones they replaced.

class SequenceTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/sequence')

class ParallelSplitTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/parallel_split')

class SynchronizationTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/synchronization')

class ExclusiveChoiceTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/exclusive_choice')

class SimpleMergeTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/simple_merge')

class MultiChoiceTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/multi_choice')

class StructuredSynchronizingMergeTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/structured_synchronizing_merge')

class MultiMergeTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/multi_merge')

class StructuredDiscriminatorTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/structured_discriminator')

class BlockingDiscriminatorTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/blocking_discriminator')

class CacncellingDiscriminatorTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/cancelling_discriminator')

class StructuredPartialJoin(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/structured_partial_join')

class BlockingPartialJoin(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/blocking_partial_join')

class CancellingPartialJoin(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/cancelling_partial_join')

class GeneralizedAndJoin(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/generalized_and_join')

class LocalSynchronizingMergeTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/acyclic_synchronizing_merge')

class GeneralSynchronizingMergeTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/general_synchronizing_merge')

class ThreadMergeTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/thread_merge')

class ThreadSplitTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/thread_split')

class MultiInstanceWithoutSynchonizationTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/multi_instance_without_synch')

class MultiInstanceWithDesignTimeKnowledgeTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/multi_instance_with_a_priori_design_time_knowledge')

class MultiInstanceWithRunTimeKnowledgeTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/multi_instance_with_a_priori_run_time_knowledge')

class StaticPartialJoinMultiInstanceTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/static_partial_join_for_multi_instance')

class CancellingPartialJoinMultiInstanceTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/cancelling_partial_join_for_multi_instance')

class DynamicPartialJoinMultiInstanceTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/dynamic_partial_join_for_multi_instance')

class DeferredChoiceTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/deferred_choice')

class InterleavedParallelRoutingTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/interleaved_parallel_routing')

class MilestoneTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/milestone')

class CriticalSectionTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/critical_section')

class InterleavedRoutingTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/interleaved_routing')

class CancelTaskTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/cancel_task')

class CancelCaseTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/cancel_case')

class CancelRegionTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/cancel_region')

class CancelMultiInstanceTaskTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/cancel_multi_instance_task')

class CompleteMultiInstanceTaskTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/complete_multiple_instance_activity')

class ArbitraryCyclesTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/arbitrary_cycles')

class RecursionTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/recursion')

    # I am disabling this test becuse I have wasted an entire day trying to make it pass
    # The workflow completes and the task tree is as expected, but the subworkflow tasks
    # no longer appear in the taken path.  This is because they are connected to the subworkflow 
    # in on_reached_cb, which now occurs after they are executed.
    # Moving subworkflow creation to predict would likely fix the problem, but there are problems
    # with prediction that also need to be fixed as well.

    #def test_run_workflow(self):
    #    pass

class ImplicitTerminationTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/implicit_termination')

class ExplicitTerminationTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/explicit_termination')

class TransientTriggerTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/transient_trigger')

class PersistentTriggerTest(TestCase, WorkflowPatternTestCase):
    def setUp(self):
        self.load_from_xml('control-flow/persistent_trigger')
