from collections import OrderedDict


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
    def __init__(self, id, label, name, typeRef):
        self.id = id
        self.label = label
        self.name = name
        self.typeRef = typeRef

class InputEntry:
    def __init__(self, id, input):
        self.id = id
        self.input = input

        self.description = ''
        self.text = ''
        self.operators = []

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
        self.parsedValue = None

class Rule:
    def __init__(self, id):
        self.id = id

        self.description = ''
        self.inputEntries = []
        self.outputEntries = []

    def outputAsDict(self):
        out = OrderedDict()
        for outputEntry in self.outputEntries:
            out[outputEntry.output.label] = outputEntry.parsedValue # TODO: label?

        return out
