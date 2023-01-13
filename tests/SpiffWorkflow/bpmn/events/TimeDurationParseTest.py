import unittest
from datetime import datetime

from SpiffWorkflow.bpmn.specs.events.event_definitions import TimerEventDefinition

class TimeDurationParseTest(unittest.TestCase):
    "Non-exhaustive ISO durations, but hopefully covers basic support"

    def test_parse_duration(self):

        valid = [
            ("P1Y6M1DT1H1M1S", {'years': 1, 'months': 6, 'days': 1, 'hours': 1, 'minutes': 1, 'seconds': 1 }),      # everything
            ("P1Y6M1DT1H1M1.5S", {'years': 1, 'months': 6, 'days': 1, 'hours': 1, 'minutes': 1, 'seconds': 1.5 }),  # fractional seconds
            ("P1YT1H1M1S", {'years': 1, 'hours': 1, 'minutes': 1, 'seconds': 1 }),                                  # minutes but no month
            ("P1MT1H", {'months': 1, 'hours':1}),                                                                   # months but no minutes
            ("P4W", {'weeks': 4}),                                                                                  # weeks
            ("P1Y6M1D", {'years': 1, 'months': 6, 'days': 1}),                                                      # no time
            ("PT1H1M1S", {'hours': 1,'minutes': 1,'seconds': 1}),                                                   # time only
            ("PT1.5H", {'hours': 1.5}),                                                                             # alt fractional
            ("T1,5H", {'hours': 1.5}),                                                                              # fractional with comma
            ("PDT1H1M1S", {'hours': 1, 'minutes': 1, 'seconds': 1}),                                                # empty spec
            ("PYMDT1H1M1S", {'hours': 1, 'minutes': 1, 'seconds': 1}),                                              # multiple empty
        ]
        for duration, parsed_duration in valid:
            result = TimerEventDefinition.parse_iso_duration(duration)
            self.assertDictEqual(result, parsed_duration)

        invalid = [
            "PT1.5H30S",    # fractional duration with subsequent non-fractional
            "PT1,5H30S",    # with comma
            "P1H1M1S",      # missing 't'
            "P1DT",         # 't' without time spec
            "P1W1D",        # conflicting day specs
            "PT1H1M1",      # trailing values
        ]
        for duration in invalid:
            self.assertRaises(Exception, TimerEventDefinition.parse_iso_duration, duration)

    def test_calculate_timedelta_from_start(self):

        start, one_day = datetime.fromisoformat("2023-01-01"), 24 * 3600
        # Leap years
        self.assertEqual(TimerEventDefinition.get_timedelta_from_start({'years': 1}, start).total_seconds(), 365 * one_day)
        self.assertEqual(TimerEventDefinition.get_timedelta_from_start({'years': 2}, start).total_seconds(), (365 + 366) * one_day)
        # Increment by month does not change day
        for month in range(1, 13):
            dt = start + TimerEventDefinition.get_timedelta_from_start({'months': month}, start)
            self.assertEqual(dt.day, 1)

    def test_calculate_timedelta_from_end(self):
        end, one_day = datetime.fromisoformat("2025-01-01"), 24 * 3600
        # Leap years
        self.assertEqual(TimerEventDefinition.get_timedelta_from_end({'years': 1}, end).total_seconds(), 366 * one_day)
        self.assertEqual(TimerEventDefinition.get_timedelta_from_end({'years': 2}, end).total_seconds(), (365 + 366) * one_day)

        dt = end - TimerEventDefinition.get_timedelta_from_end({'months': 11}, end)
        # Decrement by month does not change day
        for month in range(1, 13):
            dt = end - TimerEventDefinition.get_timedelta_from_end({'months': month}, end)
            self.assertEqual(dt.day, 1)