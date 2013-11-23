# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
from SpiffWorkflow.specs import *
from SpiffWorkflow.operators import *

class TestWorkflowSpec(WorkflowSpec):
    def __init__(self):
        WorkflowSpec.__init__(self)
        # Build one branch.
        a1 = Simple(self, 'task_a1')
        self.start.connect(a1)

        a2 = Simple(self, 'task_a2')
        a1.connect(a2)

        # Build another branch.
        b1 = Simple(self, 'task_b1')
        self.start.connect(b1)

        b2 = Simple(self, 'task_b2')
        b1.connect(b2)

        # Merge both branches (synchronized).
        synch_1 = Join(self, 'synch_1')
        a2.connect(synch_1)
        b2.connect(synch_1)

        # If-condition that does not match.
        excl_choice_1 = ExclusiveChoice(self, 'excl_choice_1')
        synch_1.connect(excl_choice_1)

        c1 = Simple(self, 'task_c1')
        excl_choice_1.connect(c1)

        c2 = Simple(self, 'task_c2')
        cond = Equal(Attrib('test_attribute1'), Attrib('test_attribute2'))
        excl_choice_1.connect_if(cond, c2)

        c3 = Simple(self, 'task_c3')
        excl_choice_1.connect_if(cond, c3)

        # If-condition that matches.
        excl_choice_2 = ExclusiveChoice(self, 'excl_choice_2')
        c1.connect(excl_choice_2)
        c2.connect(excl_choice_2)
        c3.connect(excl_choice_2)

        d1 = Simple(self, 'task_d1')
        excl_choice_2.connect(d1)

        d2 = Simple(self, 'task_d2')
        excl_choice_2.connect_if(cond, d2)

        d3 = Simple(self, 'task_d3')
        cond = Equal(Attrib('test_attribute1'), Attrib('test_attribute1'))
        excl_choice_2.connect_if(cond, d3)

        # If-condition that does not match.
        multichoice = MultiChoice(self, 'multi_choice_1')
        d1.connect(multichoice)
        d2.connect(multichoice)
        d3.connect(multichoice)

        e1 = Simple(self, 'task_e1')
        multichoice.connect_if(cond, e1)

        e2 = Simple(self, 'task_e2')
        cond = Equal(Attrib('test_attribute1'), Attrib('test_attribute2'))
        multichoice.connect_if(cond, e2)

        e3 = Simple(self, 'task_e3')
        cond = Equal(Attrib('test_attribute2'), Attrib('test_attribute2'))
        multichoice.connect_if(cond, e3)

        # StructuredSynchronizingMerge
        syncmerge = Join(self, 'struct_synch_merge_1', 'multi_choice_1')
        e1.connect(syncmerge)
        e2.connect(syncmerge)
        e3.connect(syncmerge)

        # Implicit parallel split.
        f1 = Simple(self, 'task_f1')
        syncmerge.connect(f1)

        f2 = Simple(self, 'task_f2')
        syncmerge.connect(f2)

        f3 = Simple(self, 'task_f3')
        syncmerge.connect(f3)

        # Discriminator
        discrim_1 = Join(self,
                         'struct_discriminator_1',
                         'struct_synch_merge_1',
                         threshold = 1)
        f1.connect(discrim_1)
        f2.connect(discrim_1)
        f3.connect(discrim_1)

        # Loop back to the first exclusive choice.
        excl_choice_3 = ExclusiveChoice(self, 'excl_choice_3')
        discrim_1.connect(excl_choice_3)
        cond = NotEqual(Attrib('excl_choice_3_reached'), Attrib('two'))
        excl_choice_3.connect_if(cond, excl_choice_1)

        # Split into 3 branches, and implicitly split twice in addition.
        multi_instance_1 = MultiInstance(self, 'multi_instance_1', times = 3)
        excl_choice_3.connect(multi_instance_1)

        # Parallel tasks.
        g1 = Simple(self, 'task_g1')
        g2 = Simple(self, 'task_g2')
        multi_instance_1.connect(g1)
        multi_instance_1.connect(g2)

        # StructuredSynchronizingMerge
        syncmerge2 = Join(self, 'struct_synch_merge_2', 'multi_instance_1')
        g1.connect(syncmerge2)
        g2.connect(syncmerge2)

        # Add a final task.
        last = Simple(self, 'last')
        syncmerge2.connect(last)

        # Add another final task :-).
        end = Simple(self, 'End')
        last.connect(end)
