from collections import deque
from SpiffWorkflow.Task import Task
from SpiffWorkflow.Workflow import Workflow
from SpiffWorkflow.bpmn2.specs.UserTask import UserTask
from SpiffWorkflow.specs.SubWorkflow import SubWorkflow

__author__ = 'matth'

class RouteNode(object):
    def __init__(self, task_spec, outgoing_route_node=None):
        self.task_spec = task_spec
        self.outgoing = [outgoing_route_node] if outgoing_route_node else []

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
            self.merge_routes(self.route, outgoing_route_node)
        else:
            self.route = outgoing_route_node

    def go(self, workflow):
        self._go(workflow.task_tree.children[0], self.route)

    def _go(self, task, route_node):
        assert task.task_spec == route_node.task_spec
        if route_node.outgoing:
            if not task._is_finished():
                if isinstance(task.task_spec, SubWorkflow) and task.task_spec.spec.start in [o.task_spec for o in route_node.outgoing]:
                    assert task.state == Task.READY
                    #We're going in to the subprocess
                    task.complete()
                else:
                    self.complete_task_silent(task, [n.task_spec for n in route_node.outgoing])
            for n in route_node.outgoing:
                matching_child = filter(lambda t: t.task_spec == n.task_spec, task.children)
                assert len(matching_child) == 1
                self._go(matching_child[0], n)

    def complete_task_silent(self, task, target_children_specs):
        if task._is_finished():
            return
        assert task.state == Task.READY
        task._set_state(Task.COMPLETED | (task.state & Task.TRIGGERED))
        task._update_children(target_children_specs)

    def merge_routes(self, *routes):
        #TODO: this is required for multi-threaded workflows
        raise NotImplementedError('I haven\'t done this yet')

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


class BpmnWorkflow(Workflow):

    def __init__(self, workflow_spec, name=None, **kwargs):
        super(BpmnWorkflow, self).__init__(workflow_spec, **kwargs)
        self.name = name or workflow_spec.name

    def find_task_by_name(self, target_task):
        matches = sorted(self.get_tasks_with_name(target_task), key=lambda t: t.id)
        assert len(matches) > 0
        return matches[0]

    def restore_workflow_state(self, state):
        #This currently only works for single threaded workflows
        assert self.spec.is_single_threaded()
        if state == 'COMPLETE':
            self.cancel(success=True)
            return
        s = BpmnProcessSpecState(self.spec)
        s.add_path_to_ready_task(state)
        s.go(self)


    def _get_workflow_state(self):
        assert self.spec.is_single_threaded()
        ready_tasks = self.get_tasks(state=Task.READY)
        if not ready_tasks:
            return 'COMPLETE'
        assert len(ready_tasks) == 1
        s = ready_tasks[0].task_spec.name
        w = ready_tasks[0].workflow
        while w.outer_workflow and w.outer_workflow != w:
            s = "%s:%s" % (w.name, s)
            w = w.outer_workflow
        return s

    def get_tasks_with_name(self, target_task):
        return [t for t in self.task_tree  if t.task_spec.name == target_task]

    def ready_to_end(self,end_event):

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