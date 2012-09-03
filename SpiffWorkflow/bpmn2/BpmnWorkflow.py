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

    def add_path_to_ready_task(self, full_task_name):
        task_names = full_task_name.split(':')
        #find a route passing through each task:
        route = [self.spec.start]
        for task_name in task_names[:-1]:
            route = self.breadth_first_search(task_name, route)
            route = route + [route[-1].spec.start]
        route = self.breadth_first_search(task_names[-1], route)
        assert route is not None, 'No path found for route \'%s\'' % full_task_name
        outgoing_route_node = None
        for spec in reversed(route):
            outgoing_route_node = RouteNode(spec, outgoing_route_node)
        if self.route:
            self.merge_routes(outgoing_route_node)
        else:
            self.route = outgoing_route_node

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

    def breadth_first_search(self, task_name, starting_route):
        q = deque()
        done = set()
        q.append(starting_route)
        while q:
            route = q.popleft()
            if route[-1].name == task_name and not route[-1] == starting_route[-1]:
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

    def evaluate(self, task, condition):
        return condition._matches(task)

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
        #This currently only works for single threaded workflows
        if state == 'COMPLETE':
            self.cancel(success=True)
            return
        s = BpmnProcessSpecState(self.spec)
        states = state.split(';')
        for ready_task in states:
            s.add_path_to_ready_task(ready_task)
        s.go(self)


    def _get_workflow_state(self):
        ready_tasks = self.get_tasks(state=Task.READY)
        if not ready_tasks:
            return 'COMPLETE'
        states = []
        for task in ready_tasks:
            s = task.task_spec.name
            w = task.workflow
            while w.outer_workflow and w.outer_workflow != w:
                s = "%s:%s" % (w.name, s)
                w = w.outer_workflow
            states.append(s)
        return ';'.join(sorted(states))

    def get_tasks_with_name(self, target_task):
        return [t for t in self.task_tree  if t.task_spec.name == target_task]

    def ready_to_end(self,end_event):
        #Hmm.. Should maybe be using workflow.cancel() or something here?
        complete_path = {}
        for end_task in self.get_tasks_with_name(self.spec.end.name):
            if not end_task._is_finished() and not end_task.parent == end_event:
                t = end_task
                task = end_task.parent
                while not task._is_finished():
                    complete_path.setdefault(task.id, (task, set()))[1].add(t.task_spec)
                    t = task
                    task = task.parent

        for id in sorted(complete_path.keys()):
            task, target_children_specs = complete_path[id]
            if not task._is_finished():
                self.complete_task_silent(task, list(target_children_specs))

    def redo_last_transitions(self, target_transitions):
        tasks = []
        for target_task in target_transitions.keys():
            tasks.append(self.find_task_by_name(target_task))

        complete_path = {}
        for t in tasks:
            ancestor_tasks = filter(lambda x: x.id < t.id, [self.find_task_by_name(spec.name) for spec in t.task_spec.ancestors()])

            leftover_task_set = set(ancestor_tasks)
            for task in ancestor_tasks:
                if task.parent:
                    complete_path.setdefault(task.parent.id, (task.parent, set()))[1].add(task.task_spec)
                    if task.parent in leftover_task_set:
                        leftover_task_set.remove(task.parent)
            for task in leftover_task_set:
                if task.parent:
                    complete_path.setdefault(task.id, (task, set()))[1].add(t.task_spec)

        for t in tasks:
            children = target_transitions[t.task_spec.name]
            for c in [children] if isinstance(children, basestring) else children:
                complete_path.setdefault(t.id, (t, set()))[1].add(self.get_task_spec_from_name(c))

        for id in sorted(complete_path.keys()):
            task, target_children_specs = complete_path[id]
            if not task._is_finished():
                self.complete_task_silent(task, list(target_children_specs))

    def complete_task_silent(self, task, target_children_specs):
        if task._is_finished():
            return
        assert task.state == Task.READY
        task._set_state(Task.COMPLETED | (task.state & Task.TRIGGERED))
        task._update_children(target_children_specs)

    def do_engine_steps(self):
        engine_steps = filter(lambda t: not isinstance(t.task_spec, UserTask), self.get_tasks(Task.READY))
        while engine_steps:
            for task in engine_steps:
                task.complete()
            engine_steps = filter(lambda t: not isinstance(t.task_spec, UserTask), self.get_tasks(Task.READY))

    def get_ready_user_tasks(self):
        self.do_engine_steps()
        return filter(lambda t: isinstance(t.task_spec, UserTask), self.get_tasks(Task.READY))

    def get_workflow_state(self):
        self.do_engine_steps()
        return self._get_workflow_state()