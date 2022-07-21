from SpiffWorkflow.bpmn.specs.events.event_definitions import MessageEventDefinition

class MessageEventDefinition(MessageEventDefinition):
    """
    Message Events have both a name and a payload.
    """

    # It is not entirely clear how the payload is supposed to be handled, so I have
    # deviated from what the earlier code did as little as possible, but I believe
    # this should be revisited: for one thing, we're relying on some Camunda-specific
    # properties.

    def __init__(self, name, payload=None, result_var=None):

        super(MessageEventDefinition, self).__init__(name)
        self.payload = payload
        self.result_var = result_var

        # The BPMN spec says that Messages should not be used within a process; however
        # we're doing this wrong so I am putting this here as a reminder that it should be
        # fixed, but commenting it out.

        #self.internal = False

    def catch(self, my_task, event_definition):

        # It seems very stupid to me that the sender of the message should define the
        # name of the variable the payload is saved in (the receiver ought to decide
        # what to do with it); however, Camunda puts the field on the sender, not the
        # receiver.
        if event_definition.result_var is None:
            result_var = f'{my_task.task_spec.name}_Response'
        else:
            result_var = event_definition.result_var
        my_task.internal_data[event_definition.name] = {
            "result_var": result_var,
            "payload": event_definition.payload
        }
        super(MessageEventDefinition, self).catch(my_task, event_definition)

    def throw(self, my_task):
        # We need to evaluate the message payload in the context of this task
        result = my_task.workflow.script_engine.evaluate(my_task, self.payload)
        # We can't update our own payload, because if this task is reached again
        # we have to evaluate it again so we have to create a new event
        event = MessageEventDefinition(self.name, payload=result, result_var=self.result_var)
        self._throw(event, my_task.workflow, my_task.workflow.outer_workflow)

    def reset(self, my_task):
        my_task.internal_data.pop(self.name, None)
        super(MessageEventDefinition, self).reset(my_task)

    def serialize(self):
        retdict = super().serialize()
        retdict['payload'] = self.payload
        retdict['result_var'] = self.result_var
        return retdict