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
            elif task.parent.state == TaskState.COMPLETED and task.parent.task_spec in waiting_inputs:
                waiting_inputs.remove(task.parent.task_spec)

        return len(waiting_inputs) == 0
