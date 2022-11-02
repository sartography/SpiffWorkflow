import datetime
from decimal import Decimal

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine

from ..DecisionRunner import DecisionRunner

class PythonDecisionRunner(DecisionRunner):

    def __init__(self, filename):
        scripting_additions={'Decimal': Decimal, 'datetime': datetime}
        super().__init__(PythonScriptEngine(scripting_additions=scripting_additions), filename, 'python_engine')
