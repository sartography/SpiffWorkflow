# Copyright (C) 2012 Matthew Hampton, 2023 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

from SpiffWorkflow.util.task import TaskState
from .unstructured_join import UnstructuredJoin


class ParallelGateway(UnstructuredJoin):
    """
    Task Spec for a bpmn:parallelGateway node. From the specification of BPMN
    (http://www.omg.org/spec/BPMN/2.0/PDF - document number:formal/2011-01-03):

        The Parallel Gateway is activated if there is at least one token on
        each incoming Sequence Flow.

        The Parallel Gateway consumes exactly one token from each incoming

        Sequence Flow and produces exactly one token at each outgoing
        Sequence Flow.

        TODO: Not implemented:
        If there are excess tokens at an incoming Sequence Flow, these tokens
        remain at this Sequence Flow after execution of the Gateway.

    Essentially, this means that we must wait until we have a completed parent
    task on each incoming sequence.
    """
    def _check_threshold_unstructured(self, my_task):

        tasks = my_task.workflow.get_tasks(spec_name=self.name)
        waiting_inputs = set(self.inputs)

        # The most recent instance of this spec on our own branch marks the start of the current
        # iteration, if we are in a loop at all.
        previous_iteration = my_task.find_ancestor(self.name)

        def remove_ancestor(task):
            # This traces a tasks parents until it finds a spec in the list of sources
            if task.task_spec in waiting_inputs:
                waiting_inputs.remove(task.task_spec)
            elif task.parent is not None:
                remove_ancestor(task.parent)

        for task in tasks:
            # Handle the case where the parallel gateway is part of a loop.
            if task.is_descendant_of(my_task):
                # This is the first iteration; we should not wait on this task, because it will not be reached
                # until after this join completes
                remove_ancestor(task)
            elif my_task.is_descendant_of(task):
                # This is an subsequent iteration; we need to ignore the parents of previous iterations
                continue
            # The last condition only counts inputs that arrived after the previous iteration of this
            # gateway fired.  Anything older was consumed by that iteration; typically it is a sibling
            # copy that was cancelled at the time, which is why it is neither our ancestor nor our
            # descendant and so is not caught above.  It is checked last because it walks the tree.
            elif (task.parent.state == TaskState.COMPLETED and task.parent.task_spec in waiting_inputs
                    and (previous_iteration is None or task.parent.is_descendant_of(previous_iteration))):
                waiting_inputs.remove(task.parent.task_spec)

        return len(waiting_inputs) == 0
