import os

from lxml import etree

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.dmn.engine.DMNEngine import DMNEngine
from SpiffWorkflow.dmn.parser.DMNParser import DMNParser


class DecisionRunner:
    def __init__(self, path, debug=None):
        self.path = os.path.join(os.path.dirname(__file__),
                            'data',
                            path)

        f = open(self.path, 'r')
        try:
            node = etree.parse(f)
        finally:
            f.close()
        self.dmnParser = DMNParser(None, node.getroot())
        self.dmnParser.parse()

        decision = self.dmnParser.decision
        assert len(decision.decisionTables) == 1, \
            'Exactly one decision table should exist! (%s)' \
            % (len(decision.decisionTables))

        self.dmnEngine = DMNEngine(decision.decisionTables[0], debug=debug)

    def decide(self, *inputArgs, **inputKwargs):
        return self.dmnEngine.decide(*inputArgs, **inputKwargs)
