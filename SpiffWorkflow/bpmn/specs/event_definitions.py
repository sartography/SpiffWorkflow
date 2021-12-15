# -*- coding: utf-8 -*-
from __future__ import division
from ...bpmn.PythonScriptEngine import PythonScriptEngine
from builtins import object
import datetime
# Copyright (C) 2012 Matthew Hampton
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

import sys
import datetime
import logging


LOG = logging.getLogger(__name__)


class CatchingEventDefinition(object):
    """
    The CatchingEventDefinition class is used by Catching Intermediate and
    Boundary Event tasks to know whether to proceed.
    """

    def has_fired(self, my_task):
        """
        This should return True if the event has occurred (i.e. the task may
        move from WAITING to READY). This will be called multiple times.
        """
        return my_task._get_internal_data('event_fired', False)

    def _message_ready(self, my_task):
        return False

    def _accept_message(self, my_task, message):
        return False

    def _fire(self, my_task):
        my_task._set_internal_data(event_fired=True)


class ThrowingEventDefinition(object):
    """
    This class is for future functionality. It will define the methods needed
    on an event definition that can be Thrown.
    """
    def _send_message(self, my_task, message):
        return False

class MessageEventDefinition(CatchingEventDefinition, ThrowingEventDefinition):
    """
    The MessageEventDefinition is the implementation of event definition used
    for Message Events.
    """

    def __init__(self, message,payload="",name="",resultVar=None):
        """
        Constructor.

        :param message: The message to wait for.
        """
        self.message = message
        self.payload = payload
        self.resultVar = resultVar
        self.name = name

    def has_fired(self, my_task):
        """
        Returns true if the message was received while the task was in a
        WAITING state.
        """
        return my_task._get_internal_data('event_fired', False)

    def _message_ready(self, my_task):
        waiting_messages = my_task.workflow.task_tree.internal_data.get('messages',{})
        if (self.message in waiting_messages.keys()):
            evaledpayload = waiting_messages[self.message]
            del(waiting_messages[self.message])
            return evaledpayload
        return False

    def _send_message(self, my_task,resultVar):
        payload = my_task.workflow.script_engine.evaluate(my_task, self.payload)
        my_task.workflow.message(self.message,payload,resultVar=resultVar)
        return True

    def _accept_message(self, my_task, message):
        if message != self.message:
            return False
        self._fire(my_task)
        return True

    @classmethod
    def deserialize(self, dct):
        return MessageEventDefinition(dct['message'],dct['payload'],dct['name'],dct['resultVar'])

    def serialize(self):
        retdict = {}
        module_name = self.__class__.__module__
        retdict['classname'] = module_name + '.' + self.__class__.__name__
        retdict['message'] = self.message
        retdict['payload'] = self.payload
        retdict['resultVar'] = self.resultVar
        retdict['name'] = self.name
        return retdict

class SignalEventDefinition(CatchingEventDefinition, ThrowingEventDefinition):
    """
    The MessageEventDefinition is the implementation of event definition used
    for Message Events.
    """

    def __init__(self, message,name=''):
        """
        Constructor.

        :param message: The message to wait for.
        """
        # breakpoint()
        self.message = message
        self.name = name


    def has_fired(self, my_task):
        """
        Returns true if the message was received while the task was in a
        WAITING state.
        """
        return my_task._get_internal_data('event_fired', False)

    def _message_ready(self, my_task):
        waiting_messages = my_task.workflow.task_tree.internal_data.get('signals',{})
        if (self.message in waiting_messages.keys()) :
            return (self.message,None)
        return False

    def _send_message(self, my_task):
        my_task.workflow.signal(self.message)
        return True

    def _accept_message(self, my_task, message):
        if message != self.message:
            return False
        self._fire(my_task)
        return True

    @classmethod
    def deserialize(self, dct):
        return SignalEventDefinition(dct['message'],dct['name'])

    def serialize(self):
        retdict = {}
        module_name = self.__class__.__module__
        retdict['classname'] = module_name + '.' + self.__class__.__name__
        retdict['message'] = self.message
        retdict['name'] = self.name
        return retdict


class CancelEventDefinition(CatchingEventDefinition):
    """
    The CancelEventDefinition is the implementation of event definition used
    for Cancel Events.
    """

    def __init__(self, message, name=''):
        """
        Constructor.

        :param message: The message to wait for.
        """
        self.message = message
        self.name = name

    def has_fired(self, my_task):
        """
        Returns true if the message was received while the task was in a
        WAITING state.
        """
        return my_task._get_internal_data('event_fired', False)

    def _message_ready(self, my_task):
        waiting_messages = my_task.workflow.task_tree.internal_data.get('cancels',{})
        if ('TokenReset' in waiting_messages.keys()) :
            return ('TokenReset', None)
        return False

    def _accept_message(self, my_task, message):
        if message != self.message:
            return False
        self._fire(my_task)
        return True

    @classmethod
    def deserialize(self, dct):
        return CancelEventDefinition(dct['message'],dct['name'])

    def serialize(self):
        retdict = {}
        module_name = self.__class__.__module__
        retdict['classname'] = module_name + '.' + self.__class__.__name__
        retdict['message'] = self.message
        retdict['name'] = self.name
        return retdict


class TimerEventDefinition(CatchingEventDefinition):
    """
    The TimerEventDefinition is the implementation of event definition used for
    Catching Timer Events (Timer events aren't thrown).
    """

    def __init__(self, label, dateTime):
        """
        Constructor.

        :param label: The label of the event. Used for the description.

        :param dateTime: The dateTime expression for the expiry time. This is
        passed to the Script Engine and must evaluate to a tuple in the form of
        (repeatcount,timedeltaobject)
        """
        self.label = label
        self.dateTime = dateTime

    def has_fired(self, my_task):
        """
        The Timer is considered to have fired if the evaluated dateTime
        expression is before datetime.datetime.now()
        """
        dt = my_task.workflow.script_engine.evaluate(my_task, self.dateTime)
        if isinstance(dt,datetime.timedelta):
            if my_task._get_internal_data('start_time',None) is not None:
                start_time = datetime.datetime.strptime(my_task._get_internal_data('start_time',None),'%Y-%m-%d '
                                                                                                   '%H:%M:%S.%f')
                elapsed = datetime.datetime.now() - start_time
                return elapsed > dt
            else:
                my_task.internal_data['start_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                return False

        if dt is None:
            return False
        if isinstance(dt, datetime.datetime):
            if dt.tzinfo:
                tz = dt.tzinfo
                now = tz.fromutc(datetime.datetime.utcnow().replace(tzinfo=tz))
            else:
                now = datetime.datetime.now()
        else:
            # assume type is a date, not datetime
            now = datetime.date.today()
        return now > dt

    @classmethod
    def deserialize(self, dct):
        return TimerEventDefinition(dct['label'],dct['dateTime'])

    def serialize(self):
        retdict = {}
        module_name = self.__class__.__module__
        retdict['classname'] = module_name + '.' + self.__class__.__name__
        retdict['label'] = self.label
        retdict['dateTime'] = self.dateTime
        return retdict


class EscalationEventDefinition(CatchingEventDefinition, ThrowingEventDefinition):
    """
    The EscalationEventDefinition is the implementation of event definition used for
    Escalation Events.
    """

    def __init__(self, escalation_code):
        """
        Constructor.

        :param escalation_code: The escalation code this event should
        react to. If None then all escalations will activate this event.
        """
        self.escalation_code = escalation_code

    def has_fired(self, my_task):
        """
        Returns true if the message was received while the task was in a
        WAITING state.
        """
        return my_task._get_internal_data('event_fired', False)

    def _accept_message(self, my_task, message):
        if sys.version_info[0] == 3:
            string_types = str,
        else:
            string_types = basestring,
        if isinstance(message, string_types) and message.startswith('x_escalation:'):
            parts = message.split(':')
            if len(parts) == 3:
                _, source_task_name, recv_escalation_code = parts
                if not self.escalation_code or self.escalation_code == recv_escalation_code:
                    main_child_task_spec = my_task.parent.task_spec.main_child_task_spec
                    if source_task_name == main_child_task_spec.name:
                        self._fire(my_task)
                        return True
        return False

    @classmethod
    def deserialize(self, dct):
        return EscalationEventDefinition(dct['escalation_code'])

    def serialize(self):
        retdict = {}
        module_name = self.__class__.__module__
        retdict['classname'] = module_name + '.' + self.__class__.__name__
        retdict['escalation_code'] = self.escalation_code
        return retdict





class CycleTimerEventDefinition(TimerEventDefinition):
    """
    The TimerEventDefinition is the implementation of event definition used for
    Catching Timer Events (Timer events aren't thrown).
    """


    def has_fired(self, my_task):
        """
        The Timer is considered to have fired if the evaluated dateTime
        expression is before datetime.datetime.now()
        """
        repeat,dt = my_task.workflow.script_engine.evaluate(my_task, self.dateTime)

        repeat_count = my_task._get_internal_data('repeat_count',0)

        if my_task._get_internal_data('start_time',None) is not None:
            start_time = datetime.datetime.strptime(my_task._get_internal_data('start_time',None),'%Y-%m-%d '
                                                                                                  '%H:%M:%S.%f')
            elapsed = datetime.datetime.now() - start_time
            fire = elapsed > dt
            if fire and repeat_count < repeat:
                my_task.internal_data['repeat'] = repeat
                my_task.internal_data['repeat_count'] = repeat_count + 1
                my_task.internal_data['start_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                return True
            else:
                return False
        else:
            my_task.internal_data['repeat'] = repeat
            my_task.internal_data['repeat_count'] = repeat_count
            my_task.internal_data['start_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            return False

    @classmethod
    def deserialize(self, dct):
        return CycleTimerEventDefinition(dct['label'],dct['dateTime'])

    def serialize(self):
        retdict = {}
        module_name = self.__class__.__module__
        retdict['classname'] = module_name + '.' + self.__class__.__name__
        retdict['label'] = self.label
        retdict['dateTime'] = self.dateTime
        return retdict

