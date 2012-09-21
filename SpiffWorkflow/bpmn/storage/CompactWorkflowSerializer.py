from collections import deque
import json
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnWorkflow
from SpiffWorkflow.specs import SubWorkflow
from SpiffWorkflow.storage.Serializer import Serializer

__author__ = 'matth'


class UnrecoverableWorkflowChange(Exception):
    pass

class _RouteNode(object):
    def __init__(self, task_spec, outgoing_route_node=None):
        self.task_spec = task_spec
        self.outgoing = [outgoing_route_node] if outgoing_route_node else []
        self.state = None

    def get_outgoing_by_spec(self, task_spec):
        m = filter(lambda r: r.task_spec == task_spec, self.outgoing)
        return m[0] if m else None

class _BpmnProcessSpecState(object):

    def __init__(self, spec):
        self.spec = spec
        self.route = None

    def add_path_to_transition(self, transition, state, workflow_parents):
        #find a route passing through each task:
        route = [self.spec.start]
        for task_name in workflow_parents:
            route = self._breadth_first_task_search(task_name, route)
            if route is None:
                raise UnrecoverableWorkflowChange('No path found for route \'%s\'' % transition)
            route = route + [route[-1].spec.start]
        route = self._breadth_first_transition_search(transition, route)
        if route is None:
            raise UnrecoverableWorkflowChange('No path found for route \'%s\'' % transition)
        outgoing_route_node = None
        for spec in reversed(route):
            outgoing_route_node = _RouteNode(spec, outgoing_route_node)
            outgoing_route_node.state = state
        if self.route:
            self._merge_routes(self.route, outgoing_route_node)
        else:
            self.route = outgoing_route_node

    def dump(self):
        print self.get_dump()

    def get_dump(self):
        def recursive_dump(route_node, indent, verbose=False):

            task_spec = route_node.task_spec
            dump = '%s (%s:%s)' % (task_spec.name, task_spec.__class__.__name__, hex(id(task_spec))) + '\n'
            if verbose:
                if task_spec.inputs:
                    dump += indent + '-  IN: ' + ','.join(['%s (%s)' % (t.name, hex(id(t))) for t in task_spec.inputs]) + '\n'
                if task_spec.outputs:
                    dump += indent + '- OUT: ' + ','.join(['%s (%s)' % (t.name, hex(id(t))) for t in task_spec.outputs]) + '\n'

            for i, t in enumerate(route_node.outgoing):
                dump += indent + '   --> ' + recursive_dump(t,indent+('   |   ' if i+1 < len(route_node.outgoing) else '       '))
            return dump

        dump = recursive_dump(self.route, '')
        return dump

    def go(self, workflow):
        leaf_tasks = []
        self._go(workflow.task_tree.children[0], self.route, leaf_tasks)
        for task in leaf_tasks:
            task.task_spec._update_state(task)
            task._inherit_attributes()
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
                if issubclass(task.task_spec.__class__, SubWorkflow) and task.task_spec.spec.start in [o.task_spec for o in route_node.outgoing]:
                    self._go_in_to_subworkflow(task, [n.task_spec for n in route_node.outgoing])
                else:
                    self._complete_task_silent(task, [n.task_spec for n in route_node.outgoing])
            for n in route_node.outgoing:
                matching_child = filter(lambda t: t.task_spec == n.task_spec, task.children)
                assert len(matching_child) == 1
                self._go(matching_child[0], n, leaf_tasks)

    def _complete_task_silent(self, task, target_children_specs):
        #This method simulates the completing of a task, but without hooks being called, and targeting a specific
        #subset of the children
        if task._is_finished():
            return
        task._set_state(Task.COMPLETED)

        task.children = []
        for task_spec in target_children_specs:
            task._add_child(task_spec)

    def _go_in_to_subworkflow(self, my_task, target_children_specs):
        #This method simulates the entering of a subworkflow, but without hooks being called, and targeting a specific
        #subset of the entry tasks in the subworkflow. It creates the new workflow instance and merges it in to the tree
        #This is based on SubWorkflow._on_ready_before_hook(..)
        if my_task._is_finished():
            return

        subworkflow    = my_task.task_spec._create_subworkflow(my_task)
        subworkflow.completed_event.connect(my_task.task_spec._on_subworkflow_completed, my_task)

        # Create the children (these are the tasks that follow the subworkflow, on completion:
        my_task.children = []
        my_task._sync_children(my_task.task_spec.outputs, Task.FUTURE)

        # Integrate the tree of the subworkflow into the tree of this workflow.
        for child in subworkflow.task_tree.children:
            if child.task_spec in target_children_specs:
                my_task.children.insert(0, child)
                child.parent = my_task

        my_task._set_internal_attribute(subworkflow = subworkflow)

        my_task._set_state(Task.COMPLETED)

    def _merge_routes(self, target, src):
        assert target.task_spec == src.task_spec
        for out_route in src.outgoing:
            target_out_route = target.get_outgoing_by_spec(out_route.task_spec)
            if target_out_route:
                self._merge_routes(target_out_route, out_route)
            else:
                target.outgoing.append(out_route)

    def _breadth_first_transition_search(self, transition_id, starting_route):
        return self._breadth_first_search(starting_route, transition_id=transition_id)

    def _breadth_first_task_search(self, task_name, starting_route):
        return self._breadth_first_search(starting_route, task_name=task_name)

    def _breadth_first_search(self, starting_route, task_name=None, transition_id=None):
        q = deque()
        done = set()
        q.append(starting_route)
        while q:
            route = q.popleft()
            if not route[-1] == starting_route[-1]:
                if task_name and route[-1].name == task_name:
                    return route
                if transition_id and hasattr(route[-1], 'has_outgoing_sequence_flow') and route[-1].has_outgoing_sequence_flow(transition_id):
                    route.append(route[-1].get_outgoing_sequence_flow_by_id(transition_id).task_spec)
                    return route
            for child in route[-1].outputs:
                if child not in done:
                    done.add(child)
                    q.append(route + [child])
        return None


class CompactWorkflowSerializer(Serializer):

    STATE_SPEC_VERSION = 1

    def serialize_workflow(self, workflow, include_spec=True,**kwargs):
        if include_spec:
            raise NotImplementedError('Including the spec serialization with the workflow state is not implemented.')
        return self._get_workflow_state(workflow)

    def deserialize_workflow(self, s_state, workflow_spec=None, read_only=False, **kwargs):
        if workflow_spec is None:
            raise NotImplementedError('Including the spec serialization with the workflow state is not implemented. A \'workflow_spec\' must be provided.')
        workflow = self.new_workflow(workflow_spec, read_only=read_only)
        self._restore_workflow_state(workflow, s_state)
        return workflow

    def new_workflow(self, workflow_spec, read_only=False):
        return BpmnWorkflow(workflow_spec, read_only=read_only)

    def _get_workflow_state(self, workflow):
        active_tasks = workflow.get_tasks(state=(Task.READY | Task.WAITING))
        states = []

        for task in active_tasks:
            transition = task.parent.task_spec.get_outgoing_sequence_flow_by_spec(task.task_spec).id
            w = task.workflow
            workflow_parents = []
            while w.outer_workflow and w.outer_workflow != w:
                workflow_parents.append(w.name)
                w = w.outer_workflow
            state = ("W" if task.state == Task.WAITING else "R")
            states.append([transition, workflow_parents, state])

        compacted_states = []
        for state in sorted(states, key=lambda s:",".join([s[0], s[2], (':'.join(s[1]))])):
            if state[-1] == 'R':
                state.pop()
            if state[-1] == []:
                state.pop()
            if len(state) == 1:
                state = state[0]
            compacted_states.append(state)

        state_list = compacted_states+[self.STATE_SPEC_VERSION]
        state_s = json.dumps(state_list)[1:-1]
        return state_s

    def _restore_workflow_state(self, workflow, state):
        state_list = json.loads('['+state+']')
        #We only have one version right now:
        assert state_list[-1] == self.STATE_SPEC_VERSION

        s = _BpmnProcessSpecState(workflow.spec)

        for state in state_list[:-1]:
            if isinstance(state, basestring):
                state = [state]
            transition = state[0]
            workflow_parents = state[1] if len(state)>1 else []
            state = (Task.WAITING if len(state)>2 and state[2] == 'W' else Task.READY)

            s.add_path_to_transition(transition, state, workflow_parents)

        workflow._is_busy_with_restore = True
        try:
            if len(state_list) <= 1:
                workflow.cancel(success=True)
                return
            s.go(workflow)
        finally:
            workflow._is_busy_with_restore = False
