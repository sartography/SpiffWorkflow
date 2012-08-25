from SpiffWorkflow.Task import Task
from SpiffWorkflow.Workflow import Workflow

__author__ = 'matth'

class BpmnWorkflow(Workflow):

    def find_task_by_name(self, target_task):
        matches = sorted(self.get_tasks_with_name(target_task), key=lambda t: t.id)
        self.assertGreater(len(matches), 0)
        return matches[0]

    def get_tasks_with_name(self, target_task):
        return [t for t in self.get_tasks()  if t.task_spec.name == target_task]

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
