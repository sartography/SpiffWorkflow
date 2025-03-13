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