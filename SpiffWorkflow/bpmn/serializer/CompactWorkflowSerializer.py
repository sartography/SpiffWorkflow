# -*- coding: utf-8 -*-
from builtins import str
from builtins import hex
from builtins import range
from builtins import object
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
import json
from ...task import TaskState
from ...specs import SubWorkflow
from ...serializer.base import Serializer
from ..workflow import BpmnWorkflow


class UnrecoverableWorkflowChange(Exception):
    """
    This is thrown if the workflow cannot be restored because the workflow spec
    has changed, and the identified transitions no longer exist.
    """
    pass


class _RouteNode(object):
    """
    Private helper class
    """

    def __init__(self, task_spec, outgoing_route_node=None):
        self.task_spec = task_spec
        self.outgoing = [outgoing_route_node] if outgoing_route_node else []
        self.state = None

    def get_outgoing_by_spec(self, task_spec):
        m = [r for r in self.outgoing if r.task_spec == task_spec]
        return m[0] if m else None

    def to_list(self):
        result = []
        n = self
        while n.outgoing:
            assert len(
                n.outgoing) == 1, "to_list(..) cannot be called after a merge"
            result.append(n.task_spec)
            n = n.outgoing[0]
        result.append(n.task_spec)
        return result

    def contains(self, other_route):
        if isinstance(other_route, list):
            return self.to_list()[0:len(other_route)] == other_route

        # This only works before merging
        assert len(other_route.outgoing) <= 1,\
            "contains(..) cannot be called after a merge"
        assert len(self.outgoing) <= 1,\
            "contains(..) cannot be called after a merge"

        if other_route.task_spec == self.task_spec:
            if other_route.outgoing and self.outgoing:
                return self.outgoing[0].contains(other_route.outgoing[0])
            elif self.outgoing:
                return True
            elif not other_route.outgoing:
                return True
        return False


class _BpmnProcessSpecState(object):

    """
    Private helper class
    """

    def __init__(self, spec):
        self.spec = spec
        self.route = None

    def get_path_to_transition(self, transition, state, workflow_parents,
                               taken_routes=None):
        # find a route passing through each task:
        route = [self.spec.start]
        route_to_parent_complete = None
        for task_name in workflow_parents:
            route = self._breadth_first_task_search(str(task_name), route)
            if route is None:
                raise UnrecoverableWorkflowChange(
                    'No path found for route \'%s\'' % transition)
            route_to_parent_complete = route + [route[-1].outputs[0]]
            route = route + [route[-1].spec.start]
        route = self._breadth_first_transition_search(
            transition, route, taken_routes=taken_routes)
        if route is None:
            raise UnrecoverableWorkflowChange(
                'No path found for route \'%s\'' % transition)
        outgoing_route_node = None
        for spec in reversed(route):
            outgoing_route_node = _RouteNode(spec, outgoing_route_node)
            outgoing_route_node.state = state
        return outgoing_route_node, route_to_parent_complete

    def add_route(self, outgoing_route_node):
        if self.route:
            self._merge_routes(self.route, outgoing_route_node)
        else:
            self.route = outgoing_route_node

    def dump(self):
        print(self.get_dump())

    def get_dump(self):
        def recursive_dump(route_node, indent, verbose=False):

            task_spec = route_node.task_spec
            dump = '%s (%s:%s)' % (
                task_spec.name,
                task_spec.__class__.__name__,
                hex(id(task_spec))) + '\n'
            if verbose:
                if task_spec.inputs:
                    dump += indent + '-  IN: ' + \
                        ','.join(['%s (%s)' % (t.name, hex(id(t)))
                                  for t in task_spec.inputs]) + '\n'
                if task_spec.outputs:
                    dump += indent + '- OUT: ' + \
                        ','.join(['%s (%s)' % (t.name, hex(id(t)))
                                  for t in task_spec.outputs]) + '\n'

            for i, t in enumerate(route_node.outgoing):
                dump += indent + '   --> ' + \
                    recursive_dump(
                        t, indent + (
                            '   |   ' if i + 1 < len(route_node.outgoing)
                            else '       '))
            return dump

        dump = recursive_dump(self.route, '')
        return dump

    def go(self, workflow):
        leaf_tasks = []
        self._go(workflow.task_tree.children[0], self.route, leaf_tasks)
        for task in sorted(
                leaf_tasks,
                key=lambda t: 0 if getattr(
                    t, '_bpmn_load_target_state', TaskState.READY) == TaskState.READY
                else 1):
            task.task_spec._update(task)
            task._inherit_data()
            if hasattr(task, '_bpmn_load_target_state'):
                delattr(task, '_bpmn_load_target_state')

    def _go(self, task, route_node, leaf_tasks):
        assert task.task_spec == route_node.task_spec
        if not route_node.outgoing:
            assert route_node.state is not None
            setattr(task, '_bpmn_load_target_state', route_node.state)
            leaf_tasks.append(task)
        else:
            if not task._is_finished():
                if (issubclass(task.task_spec.__class__, SubWorkflow) and
                        task.task_spec.spec.start in
                        [o.task_spec for o in route_node.outgoing]):
                    self._go_in_to_subworkflow(
                        task, [n.task_spec for n in route_node.outgoing])
                else:
                    self._complete_task_silent(
                        task, [n.task_spec for n in route_node.outgoing])
            for n in route_node.outgoing:
                matching_child = [
                    t for t in task.children if t.task_spec == n.task_spec]
                assert len(matching_child) == 1
                self._go(matching_child[0], n, leaf_tasks)

    def _complete_task_silent(self, task, target_children_specs):
        # This method simulates the completing of a task, but without hooks
        # being called, and targeting a specific subset of the children
        if task._is_finished():
            return
        task._set_state(TaskState.COMPLETED)

        task.children = []
        for task_spec in target_children_specs:
            task._add_child(task_spec)

    def _go_in_to_subworkflow(self, my_task, target_children_specs):
        # This method simulates the entering of a subworkflow, but without
        # hooks being called, and targeting a specific subset of the entry
        # tasks in the subworkflow. It creates the new workflow instance and
        # merges it in to the tree This is based on
        # SubWorkflow._on_ready_before_hook(..)
        if my_task._is_finished():
            return

        subworkflow = my_task.task_spec._create_subworkflow(my_task)
        subworkflow.completed_event.connect(
            my_task.task_spec._on_subworkflow_completed, my_task)

        # Create the children (these are the tasks that follow the subworkflow,
        # on completion:
        my_task.children = []
        my_task._sync_children(my_task.task_spec.outputs, TaskState.FUTURE)
        for t in my_task.children:
            t.task_spec._predict(t)

        # Integrate the tree of the subworkflow into the tree of this workflow.
        for child in subworkflow.task_tree.children:
            if child.task_spec in target_children_specs:
                my_task.children.insert(0, child)
                child.parent = my_task

        my_task._set_internal_data(subworkflow=subworkflow)

        my_task._set_state(TaskState.COMPLETED)

    def _merge_routes(self, target, src):
        assert target.task_spec == src.task_spec
        for out_route in src.outgoing:
            target_out_route = target.get_outgoing_by_spec(out_route.task_spec)
            if target_out_route:
                self._merge_routes(target_out_route, out_route)
            else:
                target.outgoing.append(out_route)

    def _breadth_first_transition_search(self, transition_id, starting_route,
                                         taken_routes=None):
        return self._breadth_first_search(starting_route,
                                          transition_id=transition_id,
                                          taken_routes=taken_routes)

    def _breadth_first_task_search(self, task_name, starting_route):
        return self._breadth_first_search(starting_route, task_name=task_name)

    def _breadth_first_search(self, starting_route, task_name=None,
                              transition_id=None, taken_routes=None):
        q = deque()
        done = set()
        q.append(starting_route)
        while q:
            route = q.popleft()
            if not route[-1] == starting_route[-1]:
                if task_name and route[-1].name == task_name:
                    return route
                if (transition_id and
                        hasattr(route[-1], 'has_outgoing_sequence_flow') and
                        route[-1].has_outgoing_sequence_flow(transition_id)):
                    spec = route[-1].get_outgoing_sequence_flow_by_id(
                        transition_id).target_task_spec
                    if taken_routes:
                        final_route = route + [spec]
                        for taken in taken_routes:
                            t = taken.to_list() if not isinstance(
                                taken, list) else taken
                            if final_route[0:len(t)] == t:
                                spec = None
                                break
                    if spec:
                        route.append(spec)
                        return route
            for child in route[-1].outputs:
                new_route = route + [child]
                if len(new_route) > 10000:
                    raise ValueError("Maximum looping limit exceeded "
                                     "searching for path to % s" %
                                     (task_name or transition_id))
                new_route_r = tuple(new_route)
                if new_route_r not in done:
                    done.add(new_route_r)
                    q.append(new_route)
        return None


class CompactWorkflowSerializer(Serializer):
    """
    This class provides an implementation of serialize_workflow and
    deserialize_workflow that produces a compact representation of the workflow
    state, that can be stored in a database column or reasonably small size.

    It records ONLY enough information to identify the transition leading in to
    each WAITING or READY state, along with the state of that task. This is
    generally enough to resurrect a running BPMN workflow instance, with some
    limitations.

    Limitations:
    1. The compact representation does not include any workflow or task data.
       It is the responsibility of the calling application to record whatever
       data is relevant to it, and set it on the restored workflow.
    2. The restoring process will not produce exactly the same workflow tree -
       it finds the SHORTEST route to the saved READY and WAITING tasks, not
       the route that was actually taken. This means that the tree cannot be
       interrogated for historical information about the workflow. However, the
       workflow does follow the same logic paths as would have been followed by
       the original workflow.
    """

    STATE_SPEC_VERSION = 1

    def serialize_workflow_spec(self, wf_spec, **kwargs):
        raise NotImplementedError(
            "The CompactWorkflowSerializer only supports "
            " workflow serialization.")

    def deserialize_workflow_spec(self, s_state, **kwargs):
        raise NotImplementedError(
            "The CompactWorkflowSerializer only supports "
            "workflow serialization.")

    def serialize_workflow(self, workflow, include_spec=False, **kwargs):
        """
        :param workflow: the workflow instance to serialize

        :param include_spec: Always set to False (The CompactWorkflowSerializer
        only supports workflow serialization)
        """
        if include_spec:
            raise NotImplementedError(
                'Including the spec serialization with the workflow state '
                'is not implemented.')
        return self._get_workflow_state(workflow)

    def deserialize_workflow(self, s_state, workflow_spec=None,
                             read_only=False, **kwargs):
        """
        :param s_state: the state of the workflow as returned by
        serialize_workflow

        :param workflow_spec: the Workflow Spec of the workflow
        (CompactWorkflowSerializer only supports workflow serialization)

        :param read_only: (Optional) True if the workflow should be restored in
        READ ONLY mode

        NB: Additional kwargs passed to the deserialize_workflow method will be
        passed to the new_workflow method.
        """
        if workflow_spec is None:
            raise NotImplementedError(
                'Including the spec serialization with the workflow state is '
                ' not implemented. A \'workflow_spec\' must '
                'be provided.')
        workflow = self.new_workflow(
            workflow_spec, read_only=read_only, **kwargs)
        self._restore_workflow_state(workflow, s_state)
        return workflow

    def new_workflow(self, workflow_spec, read_only=False, **kwargs):
        """
        Create a new workflow instance from the given spec and arguments.

        :param workflow_spec: the workflow spec to use

        :param read_only: this should be in read only mode

        :param kwargs: Any extra kwargs passed to the deserialize_workflow
        method will be passed through here
        """
        return BpmnWorkflow(workflow_spec, read_only=read_only, **kwargs)

    def _get_workflow_state(self, workflow):
        active_tasks = workflow.get_tasks(state=(TaskState.READY | TaskState.WAITING))
        states = []

        for task in active_tasks:
            parent_task_spec = task.parent.task_spec
            transition = parent_task_spec.get_outgoing_sequence_flow_by_spec(
                task.task_spec).id
            w = task.workflow
            workflow_parents = []
            while w.outer_workflow and w.outer_workflow != w:
                workflow_parents.append(w.name)
                w = w.outer_workflow
            state = ("W" if task.state == TaskState.WAITING else "R")
            states.append(
                [transition, list(reversed(workflow_parents)), state])

        compacted_states = []
        for state in sorted(states,
                            key=lambda s: ",".join([s[0],
                                                    s[2],
                                                    (':'.join(s[1]))])):
            if state[-1] == 'R':
                state.pop()
            if state[-1] == []:
                state.pop()
            if len(state) == 1:
                state = state[0]
            compacted_states.append(state)

        state_list = compacted_states + [self.STATE_SPEC_VERSION]
        state_s = json.dumps(state_list)[1:-1]
        return state_s

    def _restore_workflow_state(self, workflow, state):
        state_list = json.loads('[' + state + ']')

        self._check_spec_version(state_list[-1])

        s = _BpmnProcessSpecState(workflow.spec)

        routes = []
        for state in state_list[:-1]:
            if isinstance(state, str) or type(state).__name__ == 'str':
                state = [str(state)]
            transition = state[0]
            workflow_parents = state[1] if len(state) > 1 else []
            state = (TaskState.WAITING if len(state) >
                     2 and state[2] == 'W' else TaskState.READY)

            route, route_to_parent_complete = s.get_path_to_transition(
                transition, state, workflow_parents)
            routes.append(
                (route, route_to_parent_complete, transition, state,
                 workflow_parents))

        retry = True
        retry_count = 0
        while (retry):
            if retry_count > 100:
                raise ValueError(
                    'Maximum retry limit exceeded searching for unique paths')
            retry = False

            for i in range(len(routes)):
                (route, route_to_parent_complete, transition, state,
                 workflow_parents) = routes[i]

                for j in range(len(routes)):
                    if i == j:
                        continue
                    other_route = routes[j][0]
                    route_to_parent_complete = routes[j][1]
                    if route.contains(other_route) or (
                            route_to_parent_complete and route.contains(
                                route_to_parent_complete)):
                        taken_routes = [r for r in routes if r[0] != route]
                        taken_routes = [r for r in [r[0] for r
                                                    in taken_routes] +
                                        [r[1] for r in taken_routes] if r]
                        (route,
                         route_to_parent_complete) = s.get_path_to_transition(
                            transition, state, workflow_parents,
                            taken_routes=taken_routes)
                        for r in taken_routes:
                            assert not route.contains(r)
                        routes[
                            i] = (route, route_to_parent_complete, transition,
                                  state, workflow_parents)
                        retry = True
                        retry_count += 1
                        break
                if retry:
                    break

        for r in routes:
            s.add_route(r[0])

        workflow._busy_with_restore = True
        try:
            if len(state_list) <= 1:
                workflow.cancel(success=True)
                return
            s.go(workflow)
        finally:
            workflow._busy_with_restore = False

    def _check_spec_version(self, v):
        # We only have one version right now:
        assert v == self.STATE_SPEC_VERSION
