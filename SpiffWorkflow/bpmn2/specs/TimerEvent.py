import datetime
from SpiffWorkflow.bpmn2.specs.Event import Event

__author__ = 'matth'

class TimerEvent(Event):

    def __init__(self, dateTime):
        self.dateTime = dateTime

    def has_fired(self, my_task):
        if not my_task.get_attribute(self.dateTime, None):
            return False
        return datetime.datetime.now() > my_task.get_attribute(self.dateTime)


