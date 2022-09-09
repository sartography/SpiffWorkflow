# -*- coding: utf-8 -*-

import sys
import os
import unittest

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow

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

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(PythonScriptEngineTest)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
