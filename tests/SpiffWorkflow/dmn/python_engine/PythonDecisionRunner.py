from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine

from ..DecisionRunner import DecisionRunner

class PythonDecisionRunner(DecisionRunner):

    def __init__(self, filename, debug):
        super().__init__(PythonScriptEngine(), filename, 'python_engine', debug)