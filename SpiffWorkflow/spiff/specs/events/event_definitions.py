from SpiffWorkflow.bpmn.specs.events.event_definitions import MessageEventDefinition

class MessageEventDefinition(MessageEventDefinition):

    def __init__(self, name, correlation_properties=None, expression=None, message_var=None):

        super(MessageEventDefinition, self).__init__(name, correlation_properties)
        self.expression = expression
        self.message_var = message_var
        self.internal = False
        # I don't like having this here, but there's no where else to put it without a complete refactor
        self.payload = None

    def catch(self, my_task, event_definition):
        my_task.internal_data[event_definition.name] = event_definition.payload
        super(MessageEventDefinition, self).catch(my_task, event_definition)

    def throw(self, my_task):
        # We can't update our own payload, because if this task is reached again
        # we have to evaluate it again so we have to create a new event
        event = MessageEventDefinition(self.name, self.correlation_properties, self.expression, self.message_var)
        event.payload = my_task.workflow.script_engine.evaluate(my_task, self.expression)
        self._throw(event, my_task.workflow, my_task.workflow.outer_workflow)

    def reset(self, my_task):
        my_task.internal_data.pop(self.message_var, None)
        super(MessageEventDefinition, self).reset(my_task)
