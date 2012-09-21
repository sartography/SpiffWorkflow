from SpiffWorkflow.bpmn.specs.EventSpec import EventSpec

__author__ = 'matth'

class MessageEvent(EventSpec):
    """
    The MessageEvent spec is the implementation of EventSpec used for Catching Message Events.
    """

    def __init__(self, message):
        """
        Constructor.

        :param message: The message to wait for.
        """
        self.message = message

    def has_fired(self, my_task):
        """
        Returns true if the message was received while the task was in a WAITING state.
        """
        return my_task._get_internal_attribute('event_fired', False)

    def get_description(self):
        return '\'%s\'' % self.message

    def _accept_message(self, my_task, message):
        if message != self.message:
            return False
        self._fire(my_task)
        return True

    def _fire(self, my_task):
        my_task._set_internal_attribute(event_fired=True)

