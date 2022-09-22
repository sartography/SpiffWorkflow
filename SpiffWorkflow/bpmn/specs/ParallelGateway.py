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
from .UnstructuredJoin import UnstructuredJoin


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

    def _check_threshold_unstructured(self, my_task, force=False):
        completed_inputs, waiting_tasks = self._get_inputs_with_tokens(my_task)

        # If the threshold was reached, get ready to fire.
        return (force or len(completed_inputs) >= len(self.inputs),
                waiting_tasks)

    @property
    def spec_type(self):
        return 'Parallel Gateway'

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        return serializer.deserialize_generic(wf_spec, s_state, ParallelGateway)
