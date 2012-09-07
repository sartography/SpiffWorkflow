from SpiffWorkflow.bpmn2.specs.Event import Event

__author__ = 'matth'

class MessageEvent(Event):

    def __init__(self, message):
        self.message = message

    def accept_message(self, my_task, message):
        if message != self.message:
            return False
        self.fire(my_task)
        return True

    def get_description(self):
        return '\'%s\'' % self.message