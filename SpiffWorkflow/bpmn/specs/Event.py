__author__ = 'matth'

class Event(object):
    """
    The Event class is used by Catching Intermediate and Boundary Event tasks to know whether
    to proceed.
    """

    def has_fired(self, my_task):
        """
        This should return True if the event has occurred (i.e. the task may move from WAITING
        to READY). This will be called multiple times.
        """
        return my_task._get_internal_attribute('event_fired', False)

    def get_description(self):
        """
        This should return a human readable description of the event. It is used to produce a
        useful description to provide to the user.
        """
        pass

    def _accept_message(self, my_task, message):
        return False
