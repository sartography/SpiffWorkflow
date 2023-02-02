import datetime
from decimal import Decimal

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment

from ..DecisionRunner import DecisionRunner

class PythonDecisionRunner(DecisionRunner):

    def __init__(self, filename):
        environment = TaskDataEnvironment({'Decimal': Decimal, 'datetime': datetime})
        super().__init__(PythonScriptEngine(environment=environment), filename, 'python_engine')
