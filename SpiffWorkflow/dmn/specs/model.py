from collections import OrderedDict
from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine

class Decision:
    def __init__(self, id, name):
        self.id = id
        self.name = name

        self.decisionTables = []

class DecisionTable:
    def __init__(self, id, name):
        self.id = id
        self.name = name

        self.inputs = []
        self.outputs = []
        self.rules = []

class Input:
    def __init__(self, id, label, name, expression, typeRef):
        self.id = id
        self.label = label
        self.name = name
        self.expression = expression
        self.typeRef = typeRef

class InputEntry:
    def __init__(self, id, input):
        self.id = id
        self.input = input

        self.description = ''
        self.lhs = []

class Output:
    def __init__(self, id, label, name, typeRef):
        self.id = id
        self.label = label
        self.name = name
        self.typeRef = typeRef

class OutputEntry:
    def __init__(self, id, output):
        self.id = id
        self.output = output

        self.description = ''
        self.text = ''

class Rule:
    def __init__(self, id):
        self.id = id

        self.description = ''
        self.inputEntries = []
        self.outputEntries = []

    def outputAsDict(self, data):
        out = OrderedDict()
        for outputEntry in self.outputEntries:
            # try to use the id, but fall back to label if no name is provided.
            key = outputEntry.output.name or outputEntry.output.label
            if hasattr(outputEntry, "parsedRef"):
                out[key] = PythonScriptEngine().evaluate(outputEntry.parsedRef,**data)
            else:
                out[key] = ""
        return out
