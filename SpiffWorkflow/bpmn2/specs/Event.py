__author__ = 'matth'

class Event(object):

    def has_fired(self, my_task):
        return my_task._get_internal_attribute('event_fired', False)

    def fire(self, my_task):
        my_task._set_internal_attribute(event_fired=True)

    def accept_message(self, my_task, message):
        return False

    def get_description(self):
        pass

