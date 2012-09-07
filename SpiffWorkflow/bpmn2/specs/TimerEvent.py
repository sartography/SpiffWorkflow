import datetime
from SpiffWorkflow.bpmn2.specs.Event import Event

__author__ = 'matth'

class TimerEvent(Event):

    def __init__(self, label, dateTime):
        self.label = label
        self.dateTime = dateTime

    def has_fired(self, my_task):
        dt = my_task.workflow.script_engine.evaluate(my_task, self.dateTime)
        if dt is None:
            return False
        if dt.tzinfo:
            tz = dt.tzinfo
            now =  tz.fromutc(datetime.datetime.utcnow().replace(tzinfo=tz))
        else:
            now = datetime.datetime.now()
        return now > dt

    def get_description(self):
        return self.label


