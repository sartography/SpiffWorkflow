import os

from lxml import etree

from SpiffWorkflow.dmn.engine.DMNEngine import DMNEngine
from SpiffWorkflow.dmn.parser.DMNParser import DMNParser


class DecisionRunner:

    def __init__(self, script_engine, filename, path='', debug=None):
        self.script_engine = script_engine
        fn = os.path.join(os.path.dirname(__file__), path, 'data', filename)

        with open(fn) as fh:    
            node = etree.parse(fh)

        self.dmnParser = DMNParser(None, node.getroot())
        self.dmnParser.parse()

        decision = self.dmnParser.decision
        assert len(decision.decisionTables) == 1, \
            'Exactly one decision table should exist! (%s)' \
            % (len(decision.decisionTables))

        self.dmnEngine = DMNEngine(decision.decisionTables[0], debug=debug)

    def decide(self, context):
        if not isinstance(context, dict):
            context = {'input': context}
        return self.dmnEngine.decide(self.script_engine, None, context)
