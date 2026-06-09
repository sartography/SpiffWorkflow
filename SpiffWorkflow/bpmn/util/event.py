from SpiffWorkflow.task import TaskState

class BpmnEvent:
    def __init__(self, event_definition, payload=None, correlations=None, target=None):
        self.event_definition = event_definition
        self.payload = payload
        self.correlations = correlations or {}
        self.target = target


class PendingBpmnEvent:
    def __init__(self, name, event_type, value=None, correlations=None):
        self.name = name
        self.event_type = event_type
        self.value = value
        self.correlations = correlations or {}


class EventManager:

    def __init__(self, workflow):
        self.workflow = workflow
        self.tasks = {}

    def add_task(self, my_task):
        self.tasks[my_task.id] = my_task

    def remove_task(self, my_task):
        self.tasks.pop(my_task.id, None)

    def get_waiting_tasks(self):
        return [t.task_spec.event_definition.details(t) for t in self.tasks.values()]

    def catch(self, event, internal=True):
        if event.target is not None:
            # This limits results to tasks in the specified workflow
            tasks = [t for t in self.tasks.values() if t.workflow == event.target 
                     and t.task_spec.event_definition.catches(t, event)]
            if len(tasks) == 0:
                event.target = event.target.parent_workflow
                self.catch(event)
        else:
            self.update_collaboration(event)
            tasks = [t for t in self.tasks.values() if t.task_spec.catches(t, event)]
            # Figure out if we need to create an external event
            if len(tasks) == 0 and internal:
                self.workflow.bpmn_events.append(event)

        for task in tasks:
            task.task_spec.catch(task, event)
            task.task_spec._update(task)

        return len(tasks)

    def update_collaboration(self, event):

        def get_or_create_subprocess(task_spec, wf_spec):
            for sp in self.workflow.subprocesses.values():
                if sp.get_next_task(state=TaskState.WAITING, spec_name=task_spec) is not None:
                    return sp
            child_id = self.workflow.spec.start.trigger_wf(self.workflow.task_tree, wf_spec)
            return self.workflow.subprocesses[child_id]

        # Start a subprocess for known specs with start events that catch this
        for name in self.workflow.spec.start.trigger_specs:
            sp_spec = self.workflow.subprocess_specs.get(name)
            for ts in sp_spec.bpmn_start_events:
                if ts.event_definition == event.event_definition:
                    subprocess = get_or_create_subprocess(ts.name, sp_spec.name)
                    subprocess.correlations.update(event.correlations)

