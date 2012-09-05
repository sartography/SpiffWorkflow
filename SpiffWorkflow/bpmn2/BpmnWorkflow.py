from collections import deque
from SpiffWorkflow.Task import Task
from SpiffWorkflow.Workflow import Workflow
from SpiffWorkflow.bpmn2.specs.UserTask import UserTask
from SpiffWorkflow.operators import Operator
from SpiffWorkflow.specs.SubWorkflow import SubWorkflow

__author__ = 'matth'

class RouteNode(object):
    def __init__(self, task_spec, outgoing_route_node=None):
        self.task_spec = task_spec
        self.outgoing = [outgoing_route_node] if outgoing_route_node else []

    def get_outgoing_by_spec(self, task_spec):
        m = filter(lambda r: r.task_spec == task_spec, self.outgoing)
        return m[0] if m else None

class BpmnProcessSpecState(object):

    def __init__(self, spec):
        self.spec = spec
        self.route = None

    def add_path_to_transition(self, full_transition_name):
        parts = full_transition_name.split(':')
        #find a route passing through each task:
        route = [self.spec.start]
        for task_name in parts[:-1]:
            route = self.breadth_first_task_search(task_name, route)
            route = route + [route[-1].spec.start]
        route = self.breadth_first_transition_search(parts[-1], route)
        assert route is not None, 'No path found for route \'%s\'' % full_transition_name
        outgoing_route_node = None
        for spec in reversed(route):
            outgoing_route_node = RouteNode(spec, outgoing_route_node)
        if self.route:
            self.merge_routes(outgoing_route_node)
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
        self._go(workflow.task_tree.children[0], self.route)

    def _go(self, task, route_node):
        assert task.task_spec == route_node.task_spec
        if not route_node.outgoing:
            task.task_spec._update_state(task)
        else:
            if not task._is_finished():
                if isinstance(task.task_spec, SubWorkflow) and task.task_spec.spec.start in [o.task_spec for o in route_node.outgoing]:
                    task.task_spec._update_state(task)
                    assert task.state == Task.READY
                    #We're going in to the subprocess
                    task.complete()
                else:
                    self.complete_task_silent(task, [n.task_spec for n in route_node.outgoing])
            for n in route_node.outgoing:
                matching_child = filter(lambda t: t.task_spec == n.task_spec, task.children)
                if len(matching_child) != 1:
                    print matching_child
                assert len(matching_child) == 1
                self._go(matching_child[0], n)

    def complete_task_silent(self, task, target_children_specs):
        if task._is_finished():
            return
        task._set_state(Task.COMPLETED)

        task.children = []
        for task_spec in target_children_specs:
            task._add_child(task_spec)

    def merge_routes(self, new_route):
        self._merge_routes(self.route, new_route)

    def _merge_routes(self, target, src):
        assert target.task_spec == src.task_spec
        for out_route in src.outgoing:
            target_out_route = target.get_outgoing_by_spec(out_route.task_spec)
            if target_out_route:
                self._merge_routes(target_out_route, out_route)
            else:
                target.outgoing.append(out_route)

    def breadth_first_transition_search(self, transition_id, starting_route):
        return self._breadth_first_search(starting_route, transition_id=transition_id)

    def breadth_first_task_search(self, task_name, starting_route):
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

class BpmnCondition(Operator):

    def __init__(self, *args):
        if len(args) > 1:
            raise TypeError("Too many arguments")
        super(BpmnCondition, self).__init__(*args)

    def _matches(self, task):
        return task.workflow.script_engine.evaluate(task, self.args[0])


class BpmnScriptEngine(object):

    def evaluate(self, task, expression):
        if isinstance(expression, basestring):
            return task.get_attribute(expression, None)
        else:
            return expression._matches(task)

    def execute(self, task, script):
        exec script

class BpmnWorkflow(Workflow):

    def __init__(self, workflow_spec, name=None, script_engine=None, **kwargs):
        super(BpmnWorkflow, self).__init__(workflow_spec, **kwargs)
        self.name = name or workflow_spec.name
        self.script_engine = script_engine or BpmnScriptEngine()

    def accept_message(self, message):
        for my_task in Task.Iterator(self.task_tree, Task.WAITING):
            my_task.task_spec.accept_message(my_task, message)

    def find_task_by_name(self, target_task):
        matches = sorted(self.get_tasks_with_name(target_task), key=lambda t: t.id)
        assert len(matches) > 0
        return matches[0]

    def restore_workflow_state(self, state):
        if state == 'COMPLETE':
            self.cancel(success=True)
            return
        s = BpmnProcessSpecState(self.spec)
        states = state.split(';')
        for transition in states:
            s.add_path_to_transition(transition)
        s.go(self)

    def _get_workflow_state(self):
        active_tasks = self.get_tasks(state=(Task.READY | Task.WAITING))
        if not active_tasks:
            return 'COMPLETE'
        states = []
        for task in active_tasks:
            s = task.parent.task_spec.get_outgoing_sequence_flow_by_spec(task.task_spec).id
            w = task.workflow
            while w.outer_workflow and w.outer_workflow != w:
                s = "%s:%s" % (w.name, s)
                w = w.outer_workflow
            states.append(s)
        return ';'.join(sorted(states))

    def get_tasks_with_name(self, target_task):
        return [t for t in self.task_tree  if t.task_spec.name == target_task]

    def do_engine_steps(self):
        engine_steps = filter(lambda t: not isinstance(t.task_spec, UserTask), self.get_tasks(Task.READY))
        while engine_steps:
            for task in engine_steps:
                task.complete()
            engine_steps = filter(lambda t: not isinstance(t.task_spec, UserTask), self.get_tasks(Task.READY))

    def get_ready_user_tasks(self):
        self.do_engine_steps()
        return filter(lambda t: isinstance(t.task_spec, UserTask), self.get_tasks(Task.READY))

    def refresh_waiting_tasks(self):
        for my_task in self.get_tasks(Task.WAITING):
            my_task.task_spec._update_state(my_task)

    def get_waiting_tasks(self):
        self.do_engine_steps()
        return self.get_tasks(Task.WAITING)

    def get_workflow_state(self):
        self.do_engine_steps()
        return self._get_workflow_state()