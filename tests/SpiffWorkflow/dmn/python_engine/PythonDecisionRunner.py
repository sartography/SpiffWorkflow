from decimal import Decimal

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine

from ..DecisionRunner import DecisionRunner

class PythonDecisionRunner(DecisionRunner):

    def __init__(self, filename):
        super().__init__(PythonScriptEngine(scripting_additions={'Decimal': Decimal}), filename, 'python_engine')