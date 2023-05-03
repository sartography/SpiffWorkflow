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

from SpiffWorkflow.exceptions import WorkflowTaskException
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.specs.MultiChoice import MultiChoice
from .unstructured_join import UnstructuredJoin



class InclusiveGateway(MultiChoice, UnstructuredJoin):
    """
    Task Spec for a bpmn:parallelGateway node. From the specification of BPMN
    (http://www.omg.org/spec/BPMN/2.0/PDF - document number:formal/2011-01-03):

    The Inclusive Gateway is activated if
     * At least one incoming Sequence Flow has at least one token and
     * For every directed path formed by sequence flow that
        * starts with a Sequence Flow f of the diagram that has a token,
        * ends with an incoming Sequence Flow of the inclusive gateway that has
          no token, and
        * does not visit the Inclusive Gateway.
     * There is also a directed path formed by Sequence Flow that
        * starts with f,
        * ends with an incoming Sequence Flow of the inclusive gateway that has
          a token, and
        * does not visit the Inclusive Gateway.

    Upon execution, a token is consumed from each incoming Sequence Flow that
    has a token. A token will be produced on some of the outgoing Sequence
    Flows.

    TODO: Not implemented: At the moment, we can't handle having more than one
    token at a single incoming sequence
    TODO: At the moment only converging Inclusive Gateways are supported.

    In order to determine the outgoing Sequence Flows that receive a token, all
    conditions on the outgoing Sequence Flows are evaluated. The evaluation
    does not have to respect a certain order.

    For every condition which evaluates to true, a token MUST be passed on the
    respective Sequence Flow.

    If and only if none of the conditions evaluates to true, the token is
    passed on the default Sequence Flow.

    In case all conditions evaluate to false and a default flow has not been
    specified, the Inclusive Gateway throws an exception.
    """

    def test(self):
        MultiChoice.test(self)
        UnstructuredJoin.test(self)

    def _check_threshold_unstructured(self, my_task, force=False):

        completed_inputs, waiting_tasks = self._get_inputs_with_tokens(my_task)
        uncompleted_inputs = [i for i in self.inputs if i not in completed_inputs]

        # We only have to complete a task once for it to count, even if's on multiple paths
        for task in waiting_tasks:
            if task.task_spec in completed_inputs:
                waiting_tasks.remove(task)

        if force:
            # If force is true, complete the task
            complete = True
        elif len(waiting_tasks) > 0:
            # If we have waiting tasks, we're obviously not done
            complete = False
        else:
            # Handle the case where there are paths from active tasks that must go through uncompleted inputs
            tasks = my_task.workflow.get_tasks(TaskState.READY | TaskState.WAITING, workflow=my_task.workflow)
            sources = [t.task_spec for t in tasks]

            # This will go back through a task spec's ancestors and return the source, if applicable
            def check(spec): 
                for parent in spec.inputs:
                    return parent if parent in sources else check(parent)

            # If we can get to a completed input from this task, we don't have to wait for it
            for spec in completed_inputs:
                source = check(spec)
                if source is not None:
                    sources.remove(source)

            # Now check the rest of the uncompleted inputs and see if they can be reached from any of the remaining tasks
            unfinished_paths = []
            for spec in uncompleted_inputs:
                if check(spec) is not None:
                    unfinished_paths.append(spec)
                    break

            complete = len(unfinished_paths) == 0

        return complete, waiting_tasks

    def _run_hook(self, my_task):
        outputs = self._get_matching_outputs(my_task)
        if len(outputs) == 0:
            raise WorkflowTaskException(f'No conditions satisfied on gateway', task=my_task)
        my_task._sync_children(outputs, TaskState.FUTURE)
        return True

    @property
    def spec_type(self):
        return 'Inclusive Gateway'