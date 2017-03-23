# -*- coding: utf-8 -*-
from __future__ import division
from builtins import object
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

import datetime


class CatchingEventDefinition(object):

    """
    The CatchingEventDefinition class is used by Catching Intermediate and Boundary Event tasks to know whether
    to proceed.
    """

    def has_fired(self, my_task):
        """
        This should return True if the event has occurred (i.e. the task may move from WAITING
        to READY). This will be called multiple times.
        """
        return my_task._get_internal_data('event_fired', False)

    def _accept_message(self, my_task, message):
        return False

    def _fire(self, my_task):
        my_task._set_internal_data(event_fired=True)


class ThrowingEventDefinition(object):

    """
    This class is for future functionality. It will define the methods needed on an event definition
    that can be Thrown.
    """


class MessageEventDefinition(CatchingEventDefinition, ThrowingEventDefinition):

    """
    The MessageEventDefinition is the implementation of event definition used for Message Events.
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
        return my_task._get_internal_data('event_fired', False)

    def _accept_message(self, my_task, message):
        if message != self.message:
            return False
        self._fire(my_task)
        return True


class TimerEventDefinition(CatchingEventDefinition):

    """
    The TimerEventDefinition is the implementation of event definition used for Catching Timer Events
    (Timer events aren't thrown).
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
            now = tz.fromutc(datetime.datetime.utcnow().replace(tzinfo=tz))
        else:
            now = datetime.datetime.now()
        return now > dt
