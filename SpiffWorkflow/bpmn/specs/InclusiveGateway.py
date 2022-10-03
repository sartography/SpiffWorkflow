# -*- coding: utf-8 -*-

# Copyright (C) 2012 Matthew Hampton
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA
from collections import deque

from ...task import TaskState
from .UnstructuredJoin import UnstructuredJoin


class InclusiveGateway(UnstructuredJoin):
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

    @property
    def spec_type(self):
        return 'Inclusive Gateway'

    def _check_threshold_unstructured(self, my_task, force=False):

        # Look at the tree to find all ready and waiting tasks (excluding ones
        # that are our completed inputs).
        tasks = []
        for task in my_task.workflow.get_tasks(TaskState.READY | TaskState.WAITING):
            if task.thread_id != my_task.thread_id:
                continue
            if task.workflow != my_task.workflow:
                continue
            if task.task_spec == my_task.task_spec:
                continue
            tasks.append(task)

        inputs_with_tokens, waiting_tasks = self._get_inputs_with_tokens(
            my_task)
        inputs_without_tokens = [
            i for i in self.inputs if i not in inputs_with_tokens]

        waiting_tasks = []
        for task in tasks:
            if (self._has_directed_path_to(
                    task, self,
                    without_using_sequence_flow_from=inputs_with_tokens) and
                not self._has_directed_path_to(
                    task, self,
                    without_using_sequence_flow_from=inputs_without_tokens)):
                waiting_tasks.append(task)

        return force or len(waiting_tasks) == 0, waiting_tasks

    def _has_directed_path_to(self, task, task_spec,
                              without_using_sequence_flow_from=None):
        q = deque()
        done = set()

        without_using_sequence_flow_from = set(
            without_using_sequence_flow_from or [])

        q.append(task.task_spec)
        while q:
            n = q.popleft()
            if n == task_spec:
                return True
            for child in n.outputs:
                if child not in done and not (
                        n in without_using_sequence_flow_from and
                        child == task_spec):
                    done.add(child)
                    q.append(child)
        return False

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_generic(wf_spec, s_state, InclusiveGateway)
