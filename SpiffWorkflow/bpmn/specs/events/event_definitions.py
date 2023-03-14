# -*- coding: utf-8 -*-

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

import re
from datetime import datetime, timedelta, timezone
from calendar import monthrange
from time import timezone as tzoffset, altzone as dstoffset, daylight as isdst
from copy import deepcopy

from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.task import TaskState

seconds_from_utc = dstoffset if isdst else tzoffset
LOCALTZ = timezone(timedelta(seconds=-1 * seconds_from_utc))


class EventDefinition(object):
    """
    This is the base class for Event Definitions.  It implements the default throw/catch
    behavior for events.

    If internal is true, this event should be thrown to the current workflow
    If external is true, this event should be thrown to the outer workflow

    Default throw behavior is to send the event based on the values of the internal
    and external flags.
    Default catch behavior is to set the event to fired
    """
    def __init__(self):
        # Ideally I'd mke these parameters, but I don't want to them to be parameters
        # for any subclasses (as they are based on event type, not user choice) and
        # I don't want to write a separate deserializer for every every type.
        self.internal, self.external = True, True

    @property
    def event_type(self):
        return f'{self.__class__.__module__}.{self.__class__.__name__}'

    def has_fired(self, my_task):
        return my_task._get_internal_data('event_fired', False)

    def catch(self, my_task, event_definition=None):
        my_task._set_internal_data(event_fired=True)

    def throw(self, my_task):
        self._throw(
            event=my_task.task_spec.event_definition,
            workflow=my_task.workflow,
            outer_workflow=my_task.workflow.outer_workflow
        )

    def reset(self, my_task):
        my_task._set_internal_data(event_fired=False)

    def _throw(self, event, workflow, outer_workflow, correlations=None):
        # This method exists because usually we just want to send the event in our
        # own task spec, but we can't do that for message events.
        # We also don't have a more sophisticated method for addressing events to
        # a particular process, but this at least provides a mechanism for distinguishing
        # between processes and subprocesses.
        if self.external and outer_workflow != workflow:
            outer_workflow.catch(event, correlations)
        else:
            workflow.catch(event)

    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__


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


class CancelEventDefinition(EventDefinition):
    """
    Cancel events are only handled by the outerworkflow, as they can only be used inside
    of transaction subprocesses.
    """
    def __init__(self):
        super(CancelEventDefinition, self).__init__()
        self.internal = False

    @property
    def event_type(self):
        return 'Cancel'


class ErrorEventDefinition(NamedEventDefinition):
    """
    Error events can occur only in subprocesses and as subprocess boundary events.  They're
    matched by code rather than name.
    """

    def __init__(self, name, error_code=None):
        super(ErrorEventDefinition, self).__init__(name)
        self.error_code = error_code
        self.internal = False

    @property
    def event_type(self):
        return 'Error'

    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__ and self.error_code in [ None, other.error_code ]


class EscalationEventDefinition(NamedEventDefinition):
    """
    Escalation events have names, though they don't seem to be used for anything.  Instead
    the spec says that the escalation code should be matched.
    """

    def __init__(self, name, escalation_code=None):
        """
        Constructor.

        :param escalation_code: The escalation code this event should
        react to. If None then all escalations will activate this event.
        """
        super(EscalationEventDefinition, self).__init__(name)
        self.escalation_code = escalation_code

    @property
    def event_type(self):
        return 'Escalation'

    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__ and self.escalation_code in [ None, other.escalation_code ]


class CorrelationProperty:
    """Rules for generating a correlation key when a message is sent or received."""

    def __init__(self, name, retrieval_expression, correlation_keys, expected_value=None):
        self.name = name                            # This is the property name
        self.retrieval_expression = retrieval_expression  # This is how it's generated
        self.correlation_keys = correlation_keys    # These are the keys it's used by

class MessageEventDefinition(NamedEventDefinition):
    """The default message event."""

    def __init__(self, name, correlation_properties=None):
        super().__init__(name)
        self.correlation_properties = correlation_properties or []
        self.payload = None
        self.internal = False

    @property
    def event_type(self):
        return 'Message'

    def catch(self, my_task, event_definition = None):
        self.update_internal_data(my_task, event_definition)
        super(MessageEventDefinition, self).catch(my_task, event_definition)

    def throw(self, my_task):
        # We can't update our own payload, because if this task is reached again
        # we have to evaluate it again so we have to create a new event
        event = MessageEventDefinition(self.name, self.correlation_properties)
        # Generating a payload unfortunately needs to be handled using custom extensions
        # However, there needs to be something to apply the correlations to in the
        # standard case and this is line with the way Spiff works otherwise
        event.payload = deepcopy(my_task.data)
        correlations = self.get_correlations(my_task, event.payload)
        my_task.workflow.correlations.update(correlations)
        self._throw(event, my_task.workflow, my_task.workflow.outer_workflow, correlations)

    def update_internal_data(self, my_task, event_definition):
        my_task.internal_data[event_definition.name] = event_definition.payload

    def update_task_data(self, my_task):
        # I've added this method so that different message implementations can handle
        # copying their message data into the task
        payload = my_task.internal_data.get(self.name)
        if payload is not None:
            my_task.set_data(**payload)

    def get_correlations(self, task, payload):
        correlation_keys = {}
        for property in self.correlation_properties:
            for key in property.correlation_keys:
                if key not in correlation_keys:
                    correlation_keys[key] = {}
                try:
                    correlation_keys[key][property.name] = task.workflow.script_engine._evaluate(property.retrieval_expression, payload)
                except WorkflowException as we:
                    we.add_note(
                        f"Failed to evaluate correlation property '{property.name}'"
                        f" invalid expression '{property.retrieval_expression}'")
                    we.task_spec = task.task_spec
                    raise we
        return correlation_keys

    def conversation(self):
        """An event may have many correlation properties, this figures out
        which conversation exists across all of them, or return None if they
        do not share a topic. """
        conversation = None
        if len(self.correlation_properties) > 0:
            for prop in self.correlation_properties:
                for key in prop.correlation_keys:
                    conversation = key
                    for prop in self.correlation_properties:
                        if conversation not in prop.correlation_keys:
                            break
                    return conversation
        return None


class NoneEventDefinition(EventDefinition):
    """
    This class defines behavior for NoneEvents.  We override throw to do nothing.
    """
    def __init__(self):
        self.internal, self.external = False, False

    @property
    def event_type(self):
        return 'Default'

    def throw(self, my_task):
        """It's a 'none' event, so nothing to throw."""
        pass

    def reset(self, my_task):
        """It's a 'none' event, so nothing to reset."""
        pass


class SignalEventDefinition(NamedEventDefinition):
    """The SignalEventDefinition is the implementation of event definition used for Signal Events."""

    @property
    def spec_type(self):
        return 'Signal'

class TerminateEventDefinition(EventDefinition):
    """The TerminateEventDefinition is the implementation of event definition used for Termination Events."""

    def __init__(self):
        super(TerminateEventDefinition, self).__init__()
        self.external = False

    @property
    def event_type(self):
        return 'Terminate'


class TimerEventDefinition(EventDefinition):

    def __init__(self, name, expression):
        """
        Constructor.

        :param name: The description of the timer.

        :param expression: An ISO 8601 datetime or interval expression.
        """
        super().__init__()
        self.name = name
        self.expression = expression

    @staticmethod
    def get_datetime(expression):
        dt = datetime.fromisoformat(expression)
        if dt.tzinfo is None:
            dt = datetime.combine(dt.date(), dt.time(), LOCALTZ)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def get_timedelta_from_start(parsed_duration, start=None):

        start = start or datetime.now(timezone.utc)
        years, months, days = parsed_duration.pop('years', 0), parsed_duration.pop('months', 0), parsed_duration.pop('days', 0)
        months += years * 12

        for idx in range(int(months)):
            year, month = start.year + idx // 12, start.month + idx % 12
            days += monthrange(year, month)[1]

        year, month = start.year + months // 12, start.month + months % 12
        days += (months - int(months)) * monthrange(year, month)[1]
        parsed_duration['days'] = days
        return timedelta(**parsed_duration)

    @staticmethod
    def get_timedelta_from_end(parsed_duration, end):

        years, months, days = parsed_duration.pop('years', 0), parsed_duration.pop('months', 0), parsed_duration.pop('days', 0)
        months += years * 12

        for idx in range(1, int(months) + 1):
            year = end.year - (1 + (idx - end.month) // 12)
            month = 1 + (end.month - idx - 1) % 12
            days += monthrange(year, month)[1]

        days += (months - int(months)) * monthrange(
            end.year - (1 + (int(months)- end.month) // 12),
            1 + (end.month - months - 1) % 12)[1]
        parsed_duration['days'] = days
        return timedelta(**parsed_duration)

    @staticmethod
    def parse_iso_duration(expression):

        # Based on https://en.wikipedia.org/wiki/ISO_8601#Time_intervals
        parsed, expr_t, current = {}, False, expression.lower().strip('p').replace(',', '.')
        for designator in ['years', 'months', 'weeks', 'days', 't', 'hours', 'minutes', 'seconds']:
            value = current.split(designator[0], 1)
            if len(value) == 2:
                duration, remainder = value
                if duration.isdigit():
                    parsed[designator] = int(duration)
                elif duration.replace('.', '').isdigit() and not remainder:
                    parsed[designator] = float(duration)
                if designator in parsed or designator == 't':
                    current = remainder
                if designator == 't':
                    expr_t = True

        date_specs, time_specs = ['years', 'months', 'days'], ['hours', 'minutes', 'seconds']
        parsed_t = len([d for d in parsed if d in time_specs]) > 0

        if len(current) or parsed_t != expr_t or ('weeks' in parsed and any(v for v in parsed if v in date_specs)):
            raise Exception('Invalid duration')
        # The actual timedelta will have to be computed based on a start or end date, to account for
        # months lengths, leap days, etc.  This returns a dict of the parsed elements
        return parsed

    @staticmethod
    def parse_iso_week(expression):
        # https://en.wikipedia.org/wiki/ISO_8601#Week_dates
        m = re.match('(\d{4})W(\d{2})(\d)(T.+)?', expression.upper().replace('-', ''))
        year, month, day, ts = m.groups()
        ds = datetime.fromisocalendar(int(year), int(month), int(day)).strftime('%Y-%m-%d')
        return TimerEventDefinition.get_datetime(ds + (ts or ''))

    @staticmethod
    def parse_time_or_duration(expression):
        if expression.upper().startswith('P'):
            return TimerEventDefinition.parse_iso_duration(expression)
        elif 'W' in expression.upper():
            return TimerEventDefinition.parse_iso_week(expression)
        else:
            return TimerEventDefinition.get_datetime(expression)

    @staticmethod
    def parse_iso_recurring_interval(expression):
        components = expression.upper().replace('--', '/').strip('R').split('/')
        cycles = int(components[0]) if components[0] else -1
        start_or_duration = TimerEventDefinition.parse_time_or_duration(components[1])
        if len(components) == 3:
            end_or_duration = TimerEventDefinition.parse_time_or_duration(components[2])
        else:
            end_or_duration = None

        if isinstance(start_or_duration, datetime):
            # Start time + interval duration
            start = start_or_duration
            duration = TimerEventDefinition.get_timedelta_from_start(end_or_duration, start_or_duration)
        elif isinstance(end_or_duration, datetime):
            # End time + interval duration
            duration = TimerEventDefinition.get_timedelta_from_end(start_or_duration, end_or_duration)
            start = end_or_duration - duration
        elif end_or_duration is None:
            # Just an interval duration, assume a start time of now
            start = datetime.now(timezone.utc)
            duration = TimeDateEventDefinition.get_timedelta_from_start(start_or_duration, start)
        else:
            raise Exception("Invalid recurring interval")
        return cycles, start, duration

    def __eq__(self, other):
        return self.__class__.__name__ == other.__class__.__name__ and self.name == other.name


class TimeDateEventDefinition(TimerEventDefinition):
    """A Timer event represented by a specific date/time."""

    @property
    def event_type(self):
        return 'Time Date Timer'

    def has_fired(self, my_task):
        event_value = my_task._get_internal_data('event_value')
        if event_value is None:
            event_value = my_task.workflow.script_engine.evaluate(my_task, self.expression)
            my_task._set_internal_data(event_value=event_value)
        if TimerEventDefinition.parse_time_or_duration(event_value) < datetime.now(timezone.utc):
            my_task._set_internal_data(event_fired=True)
        return my_task._get_internal_data('event_fired', False)

    def timer_value(self, my_task):
        return my_task._get_internal_data('event_value')


class DurationTimerEventDefinition(TimerEventDefinition):
    """A timer event represented by a duration"""

    @property
    def event_type(self):
        return 'Duration Timer'

    def has_fired(self, my_task):
        event_value = my_task._get_internal_data("event_value")
        if event_value is None:
            expression = my_task.workflow.script_engine.evaluate(my_task, self.expression)
            parsed_duration = TimerEventDefinition.parse_iso_duration(expression)
            event_value = (datetime.now(timezone.utc) + TimerEventDefinition.get_timedelta_from_start(parsed_duration)).isoformat()
            my_task._set_internal_data(event_value=event_value)
        if TimerEventDefinition.get_datetime(event_value) < datetime.now(timezone.utc):
            my_task._set_internal_data(event_fired=True)
        return my_task._get_internal_data('event_fired', False)

    def timer_value(self, my_task):
        return my_task._get_internal_data("event_value")


class CycleTimerEventDefinition(TimerEventDefinition):

    @property
    def event_type(self):
        return 'Cycle Timer'

    def has_fired(self, my_task):

        if not my_task._get_internal_data('event_fired'):
            # Only check for the next cycle when the event has not fired to prevent cycles from being skipped.
            event_value = my_task._get_internal_data('event_value')
            if event_value is None:
                expression = my_task.workflow.script_engine.evaluate(my_task, self.expression)
                cycles, start, duration = TimerEventDefinition.parse_iso_recurring_interval(expression)
                event_value = {'cycles': cycles, 'next': start.isoformat(), 'duration': duration.total_seconds()}

            if event_value['cycles'] > 0:
                next_event = datetime.fromisoformat(event_value['next'])
                if next_event < datetime.now(timezone.utc):
                    my_task._set_internal_data(event_fired=True)
                    event_value['next'] = (next_event + timedelta(seconds=event_value['duration'])).isoformat()

            my_task._set_internal_data(event_value=event_value)

        return my_task._get_internal_data('event_fired', False)

    def timer_value(self, my_task):
        event_value = my_task._get_internal_data('event_value')
        if event_value is not None and event_value['cycles'] > 0:
            return event_value['next']

    def complete(self, my_task):
        event_value = my_task._get_internal_data('event_value')
        if event_value is not None and event_value['cycles'] == 0:
            my_task.internal_data.pop('event_value')
            return True

    def complete_cycle(self, my_task):
        # Only increment when the task completes
        if my_task._get_internal_data('event_value') is not None:
            my_task.internal_data['event_value']['cycles'] -= 1


class MultipleEventDefinition(EventDefinition):

    def __init__(self, event_definitions=None, parallel=False):
        super().__init__()
        self.event_definitions = event_definitions or []
        self.parallel = parallel

    @property
    def event_type(self):
        return 'Multiple'

    def has_fired(self, my_task):

        seen_events = my_task.internal_data.get('seen_events', [])
        for event in self.event_definitions:
            if isinstance(event, (TimerEventDefinition, CycleTimerEventDefinition)):
                child = [c for c in my_task.children if c.task_spec.event_definition == event]
                child[0].task_spec._update_hook(child[0])
                child[0]._set_state(TaskState.MAYBE)
                if event.has_fired(my_task):
                    seen_events.append(event)

        if self.parallel:
            # Parallel multiple need to match all events
            return all(event in seen_events for event in self.event_definitions)
        else:
            return len(seen_events) > 0

    def catch(self, my_task, event_definition=None):
        event_definition.catch(my_task, event_definition)
        seen_events = my_task.internal_data.get('seen_events', []) + [event_definition]
        my_task._set_internal_data(seen_events=seen_events)

    def reset(self, my_task):
        my_task.internal_data.pop('seen_events', None)
        super().reset(my_task)

    def __eq__(self, other):
        # This event can catch any of the events associated with it
        for event in self.event_definitions:
            if event == other:
                return True
        return False

    def throw(self, my_task):
        # Mutiple events throw all associated events when they fire
        for event_definition in self.event_definitions:
            self._throw(
                event=event_definition,
                workflow=my_task.workflow,
                outer_workflow=my_task.workflow.outer_workflow
            )
