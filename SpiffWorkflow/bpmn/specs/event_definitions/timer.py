import re
from datetime import datetime, timedelta, timezone
from calendar import monthrange
from time import timezone as tzoffset, altzone as dstoffset, struct_time, localtime

from SpiffWorkflow.util.task import TaskState
from SpiffWorkflow.bpmn.util import PendingBpmnEvent
from .base import EventDefinition

seconds_from_utc = dstoffset if struct_time(localtime()).tm_isdst else tzoffset
LOCALTZ = timezone(timedelta(seconds=-1 * seconds_from_utc))

class TimerEventDefinition(EventDefinition):

    def __init__(self, name, expression, **kwargs):
        """
        Constructor.

        :param name: The description of the timer.
        :param expression: An ISO 8601 datetime or interval expression.
        """
        super().__init__(**kwargs)
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
            year = start.year + (start.month + idx - 1) // 12
            month = (start.month + idx) % 12 or 12
            days += monthrange(year, month)[1]

        year = start.year + (start.month + months - 1) // 12
        month = (start.month + months) % 12 or 12
        days += (months - int(months)) * monthrange(year, month)[1]

        parsed_duration['days'] = days
        return timedelta(**parsed_duration)

    @staticmethod
    def get_timedelta_from_end(parsed_duration, end):

        years, months, days = parsed_duration.pop('years', 0), parsed_duration.pop('months', 0), parsed_duration.pop('days', 0)
        months += years * 12

        for idx in range(1, int(months) + 1):
            year = end.year - (1 + (idx - end.month) // 12)
            month = (end.month - idx) % 12 or 12
            days += monthrange(year, month)[1]

        year = end.year - (1 + (months - end.month) // 12)
        month = (end.month - months) % 12 or 12
        days += (months - int(months)) * monthrange(year, month)[1]

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
        m = re.match(r'(\d{4})W(\d{2})(\d)(T.+)?', expression.upper().replace('-', ''))
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
            # Just an interval duration, assume a start time of now + duration
            duration = TimeDateEventDefinition.get_timedelta_from_start(start_or_duration)
            start = datetime.now(timezone.utc) + duration
        else:
            raise Exception("Invalid recurring interval")
        return cycles, start, duration

    def __eq__(self, other):
        return super().__eq__(other) and self.name == other.name


class TimeDateEventDefinition(TimerEventDefinition):
    """A Timer event represented by a specific date/time."""

    def has_fired(self, my_task):
        event_value = my_task._get_internal_data('event_value')
        if event_value is None:
            event_value = my_task.workflow.script_engine.evaluate(my_task, self.expression)
            my_task._set_internal_data(event_value=event_value)
        if TimerEventDefinition.parse_time_or_duration(event_value) < datetime.now(timezone.utc):
            my_task._set_internal_data(event_fired=True)
        return my_task._get_internal_data('event_fired', False)

    def details(self, my_task):
        return PendingBpmnEvent(self.name, self.__class__.__name__, my_task._get_internal_data('event_value'))


class DurationTimerEventDefinition(TimerEventDefinition):
    """A timer event represented by a duration"""

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

    def details(self, my_task):
        return PendingBpmnEvent(self.name, self.__class__.__name__, my_task._get_internal_data('event_value'))


class CycleTimerEventDefinition(TimerEventDefinition):

    def cycle_complete(self, my_task):

        event_value = my_task._get_internal_data('event_value')
        if event_value is None:
            expression = my_task.workflow.script_engine.evaluate(my_task, self.expression)
            cycles, start, duration = TimerEventDefinition.parse_iso_recurring_interval(expression)
            event_value = {'cycles': cycles, 'next': start.isoformat(), 'duration': duration.total_seconds()}

        # When the next timer event passes, return True to allow the parent task to generate another child
        # Use event fired to indicate that this timer has completed all cycles and the task can be completed
        ready = False
        if event_value['cycles'] != 0:
            next_event = datetime.fromisoformat(event_value['next'])
            if next_event < datetime.now(timezone.utc):
                event_value['next'] = (next_event + timedelta(seconds=event_value['duration'])).isoformat()
                event_value['cycles'] -= 1
                ready = True
        else:
            my_task.internal_data.pop('event_value', None)
            my_task.internal_data['event_fired'] = True

        my_task._set_internal_data(event_value=event_value)
        return ready

    def update_task(self, my_task):
        if self.cycle_complete(my_task):
            for output in my_task.task_spec.outputs:
                child = my_task._add_child(output, TaskState.FUTURE)
                child.task_spec._predict(child, mask=TaskState.NOT_FINISHED_MASK)
                child.task_spec._update(child)

    def details(self, my_task):
        event_value = my_task._get_internal_data('event_value')
        if event_value is not None and event_value['cycles'] != 0:
            event_value = event_value['next']
        return PendingBpmnEvent(self.name, self.__class__.__name__, event_value)
