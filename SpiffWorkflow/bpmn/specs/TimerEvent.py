import datetime
from SpiffWorkflow.bpmn.specs.EventSpec import EventSpec

__author__ = 'matth'

class TimerEvent(EventSpec):
    """
    The TimerEvent spec is the implementation of EventSpec used for Catching Timer Events.
    """

    def __init__(self, label, dateTime):
        """
        Constructor.

        :param label: The label of the event. Used for the description.
        :param dateTime: The dateTime expression for the expiry time. This is passed to the Script Engine and
        must evaluate to a datetime.datetime instance.
        """
        self.label = label
        self.dateTime = dateTime

    def has_fired(self, my_task):
        """
        The Timer is considered to have fired if the evaluated dateTime expression is before datetime.datetime.now()
        """
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


