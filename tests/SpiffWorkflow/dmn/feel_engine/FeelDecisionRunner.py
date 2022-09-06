from SpiffWorkflow.bpmn.FeelLikeScriptEngine import FeelLikeScriptEngine

from ..DecisionRunner import DecisionRunner

class FeelDecisionRunner(DecisionRunner):

    def __init__(self, filename):
        super().__init__(FeelLikeScriptEngine(), filename, 'feel_engine')