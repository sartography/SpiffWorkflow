# -*- coding: utf-8 -*-

import sys
import os
import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine, Box
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.spiff.specs import NoneTask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from tests.SpiffWorkflow.bpmn.BpmnWorkflowTestCase import BpmnWorkflowTestCase

__author__ = 'danfunk'


class PythonScriptEngineTest(BpmnWorkflowTestCase):

    def setUp(self):
        self.expressionEngine = PythonScriptEngine()

    def testDateTimeExpressions(self):
        """Basically, assure that we can use datime, dateutils, and pytz"""
        script = """
# Create Current Date as UTC
now_utc = datetime.datetime.now(datetime.timezone.utc)
# Create Current Date at EST
now_est = now_utc.astimezone(pytz.timezone('US/Eastern'))

# Format a date from a date String in UTC
datestr = "2021-09-23 16:11:00 -0000"  # 12 pm EST,  4pm UTC
dt = dateparser.parse(datestr)
localtime = dt.astimezone(pytz.timezone('US/Eastern'))
localtime_str = localtime.strftime("%Y-%m-%d %H:%M:%S")
        """
        # In a workflow this happens automatically
        data = {}
        self.expressionEngine._execute(script, data)
        self.assertEqual(data['now_utc'].utcoffset().days, 0)
        self.assertEqual(data['now_est'].tzinfo.zone, "US/Eastern")
        self.assertEqual(data['localtime_str'], "2021-09-23 12:11:00")
        self.assertTrue(True)

    def testConvertToBox(self):
        """assure we are exercising this function fully in the tests"""
        data = {
            'x': 1,
            'y': {'a': 2},
            'z': [{'a': 'apple'}, {'b': 'bannana'}]
        }
        boxed_data = PythonScriptEngine().convert_to_box(data)
        self.assertEqual(1, boxed_data.x)
        self.assertEqual(2, boxed_data.y.a)
        # This doesn't feel right o me, seems like we should be able
        # to use dot notation here as well.
        self.assertEqual('apple', boxed_data.z[0]['a'])

    def test_box_construction_with_kwargs(self):
        """assure we are exercising this part of the code in the tests"""
        my_box = Box(a="apple", b={"b": "banana"})
        self.assertEqual('apple', my_box.a)
        self.assertEqual('banana', my_box.b.b)

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PythonScriptEngineTest)


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
