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

    def __init__(self):
        self.tasks = {}

    def add_task(self, my_task):
        self.tasks[my_task.id] = my_task

    def remove_task(self, my_task):
        self.tasks.pop(my_task, None)


