# -*- coding: utf-8 -*-
from __future__ import division
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
import datetime

from ....bpmn.PythonScriptEngine import PythonScriptEngine

from builtins import object

LOG = logging.getLogger(__name__)


class EventDefinition(object):
    """
    This is the base class for Event Definitions.  It implements the default throw/catch
    behavior for events.

    If internal is true, this event should be thrown to the current workflow
    If external is true, this event should be thrown to the outer workflow

    Default throw behavior is to send the event to the current workflow
    Default catch behavior is to set the event to fired
    """

    def __init__(self):
        # Ideally I'd mke these parameters, but I don't want to them to be parameters
        # for any subclasses (as they are based on event type, not user choice) and
        # I don't want to write a separate deserializer for every every type.
        self.internal, self.external = True, True

    def has_fired(self, my_task):
        return my_task._get_internal_data('event_fired', False)

    def catch(self, my_task, event_definition=None):
        my_task._set_internal_data(event_fired=True) 

    def throw(self, event_definition, workflow):
        workflow.catch(event_definition)

    def reset(self, my_task):
        my_task._set_internal_data(event_fired=False)

    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__

    def serialize(self):
        return { 
            'classname': self.__class__.__module__ + '.' + self.__class__.__name__,
            'internal': self.internal,
            'external': self.external,
        }

    @classmethod
    def deserialize(cls, dct):
        cls_name = dct.pop('classname')
        internal, external = dct.pop('internal'), dct.pop('external')
        obj = cls(**dct)
        obj.internal, obj.external = internal, external
        return obj

class NamedEventDefinition(EventDefinition):
    """
    Extend the base event class to provide a name for the event.  Most throw/catch events
    have names that names that will be used to identify the event.

    :param name: the name of this event
    """

    def __init__(self, name):
        super(NamedEventDefinition, self).__init__()
        self.name = name

    def reset(self, my_task):
        super(NamedEventDefinition, self).reset(my_task)

    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__ and self.name == other.name

    def serialize(self):
        retdict = super(NamedEventDefinition, self).serialize()
        retdict['name'] = self.name
        return retdict


class CancelEventDefinition(EventDefinition):
    """
    Cancel events are only handled by the outerworkflow, as they can only be used inside
    of transaction subprocesses.
    """
    def __init__(self):
        super(CancelEventDefinition, self).__init__()
        self.internal = False


class EscalationEventDefinition(NamedEventDefinition):
    """
    Escalation events have names, though they don't seem to be used for anything.  Instead
    the spec says that the escaltion code should be matched.
    """

    def __init__(self, name, escalation_code=None):
        """
        Constructor.

        :param escalation_code: The escalation code this event should
        react to. If None then all escalations will activate this event.
        """
        super(EscalationEventDefinition, self).__init__(name)
        self.escalation_code = escalation_code

    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__ and self.escalation_code in [ None, other.escalation_code ]

    def serialize(self):
        retdict = super(EscalationEventDefinition, self).serialize()
        retdict['escalation_code'] = self.escalation_code
        return retdict


class MessageEventDefinition(NamedEventDefinition):
    """
    Message Events have both a name and a payload.

    It is not entirely clear how the payload is supposed to be handled, so I have 
    deviated from what the earlier code did as little as possible, but I believe
    this should be revisited: for one thing, we're relying on some Camunda-sepcific
    properties.
    """

    def __init__(self, name, payload=None, result_var=None):

        # Internal should be false according to the BPMN spec, and we use it incorrectly
        super(MessageEventDefinition, self).__init__(name)
        self.payload = payload
        self.result_var = result_var if result_var is not None else f'{name}_result'

        # The BPMN spec says that Messages should not be used within a process; however
        # we're doing this wrong so I am putting this here as a reminder, but commenting
        # it out.

        #self.internal = False

    def catch(self, my_task, event_definition):

        my_task.internal_data[event_definition.name] = event_definition.result_var, event_definition.payload
        super(MessageEventDefinition, self).catch(my_task, event_definition)

    def throw(self, my_task, workflow):
        # We need to evaluate the message payload in the context of this task
        result = my_task.workflow.script_engine.evaluate(my_task, self.payload)
        # We can't update our own payload, because if this task is reached again
        # we have to evaluate it again.
        # I don't like this, but I also don't want to write a separate class just
        # for this special case (where the thrown/caught event are identical)
        # especially as we're doing this all wrong anyway.
        event = MessageEventDefinition(self.name, payload=result, result_var=self.result_var)
        super(MessageEventDefinition, self).throw(event, workflow)

    def reset(self, my_task):
        my_task.internal_data.pop(self.name, None)
        super(MessageEventDefinition, self).reset(my_task)

    def serialize(self):
        retdict = super(MessageEventDefinition, self).serialize()
        retdict['payload'] = self.payload
        retdict['result_var'] = self.result_var
        return retdict


class NoneEventDefinition(EventDefinition):
    """
    This class defines behavior for NoneEvents.  We override throw to do nothing.
    """

    def __init__(self):
        self.internal = False
        self.external = False

    def throw(self, my_task, workflow):
        pass

    def reset(self, my_task):
        pass


class SignalEventDefinition(NamedEventDefinition):
    """The SignalEventDefinition is the implementation of event definition used for Signal Events."""
    
    def __init__(self, name):
        super(SignalEventDefinition, self).__init__(name)


class TerminateEventDefinition(EventDefinition):
    """The TerminateEventDefinition is the implementation of event definition used for Termination Events."""
    
    def __init__(self):
        super(TerminateEventDefinition, self).__init__()
        self.external = False

class TimerEventDefinition(EventDefinition):
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
        super(TimerEventDefinition, self).__init__()
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
    def deserialize(cls, dct):
        return TimerEventDefinition(dct['label'],dct['dateTime'])

    def serialize(self):
        retdict = super(TimerEventDefinition, self).serialize()
        retdict['label'] = self.label
        retdict['dateTime'] = self.dateTime
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
    def deserialize(cls, dct):
        return CycleTimerEventDefinition(dct['label'],dct['dateTime'])
