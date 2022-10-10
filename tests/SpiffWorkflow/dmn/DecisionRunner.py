import os

from lxml import etree

from SpiffWorkflow.bpmn.PythonScriptEngine import Box
from SpiffWorkflow.dmn.engine.DMNEngine import DMNEngine
from SpiffWorkflow.dmn.parser.DMNParser import DMNParser


class Workflow:
    def __init__(self, script_engine):
        self.script_engine = script_engine
        self.outer_workflow = self
        self.spec = Box({'file': 'my_mock_file'})

class TaskSpec:
    def __init__(self):
        self.name = "MockTestSpec"
        self.description = "Mock Test Spec"

class Task:
    def __init__(self, script_engine, data):
        self.data = data
        self.workflow = Workflow(script_engine)
        self.task_spec = TaskSpec()

class DecisionRunner:

    def __init__(self, script_engine, filename, path=''):
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

        self.dmnEngine = DMNEngine(decision.decisionTables[0])

    def decide(self, context):

        if not isinstance(context, dict):
            context = {'input': context}
        task = Task(self.script_engine, context)
        return self.dmnEngine.decide(task)
