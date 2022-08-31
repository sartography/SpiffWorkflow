from SpiffWorkflow.bpmn.specs.events.event_definitions import MessageEventDefinition

class MessageEventDefinition(MessageEventDefinition):

    def __init__(self, name, correlation_properties=None, expression=None, message_var=None):

        super(MessageEventDefinition, self).__init__(name, correlation_properties)
        self.expression = expression
        self.message_var = message_var
        self.internal = False

    def throw(self, my_task):
        # We can't update our own payload, because if this task is reached again
        # we have to evaluate it again so we have to create a new event
        event = MessageEventDefinition(self.name, self.correlation_properties, self.expression, self.message_var)
        event.payload = my_task.workflow.script_engine.evaluate(my_task, self.expression)
        correlations = self.get_correlations(my_task.workflow.script_engine, event.payload)
        my_task.workflow.correlations.update(correlations)
        self._throw(event, my_task.workflow, my_task.workflow.outer_workflow, correlations)

    def update_task_data(self, my_task):
        my_task.data[self.message_var] = my_task.internal_data[self.name]

    def reset(self, my_task):
        my_task.internal_data.pop(self.message_var, None)
        super(MessageEventDefinition, self).reset(my_task)
