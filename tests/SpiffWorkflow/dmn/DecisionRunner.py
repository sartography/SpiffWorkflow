import os

from lxml import etree

from SpiffWorkflow.dmn.engine.DMNEngine import DMNEngine
from SpiffWorkflow.dmn.parser.DMNParser import DMNParser
from SpiffWorkflow.bpmn.parser.node_parser import DEFAULT_NSMAP

class WorkflowSpec:
    def __init__(self):
        self.file = 'my_mock_file'
        self.name = 'Mock Workflow Spec'
        self.task_specs = {}

class Workflow:
    def __init__(self, script_engine):
        self.script_engine = script_engine
        self.parent = None
        self.spec = WorkflowSpec()
        self.top_workflow = self

class TaskSpec:
    def __init__(self):
        self.name = "MockTestSpec"
        self.bpmn_name = "Mock Test Spec"

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

        nsmap = DEFAULT_NSMAP.copy()
        nsmap.update(node.getroot().nsmap)
        if None in nsmap:
            nsmap['dmn'] = nsmap.pop(None)

        self.dmnParser = DMNParser(None, node.getroot(), nsmap)
        self.dmnParser.parse()

        decision = self.dmnParser.decision
        assert len(decision.decisionTables) == 1, \
            'Exactly one decision table should exist! (%s)' \
            % (len(decision.decisionTables))

        self.decision_table = decision.decisionTables[0]
        self.dmnEngine = DMNEngine(self.decision_table)

    def decide(self, context):
        """Makes the rather ugly assumption that there is only one
         rule match for a decision - which was previously the case"""
        if not isinstance(context, dict):
            context = {'input': context}
        task = Task(self.script_engine, context)
        return self.dmnEngine.decide(task)[0]

    def result(self, context):
        task = Task(self.script_engine, context)
        return self.dmnEngine.result(task)
