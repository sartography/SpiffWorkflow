from collections import OrderedDict
from enum import Enum

from ...util.deep_merge import DeepMerge


class HitPolicy(Enum):
    UNIQUE = "UNIQUE"
    COLLECT = "COLLECT"
    # ANY = "ANY"
    # PRIORITY = "PRIORITY"
    # FIRST = "FIRST"
    # OUTPUT_ORDER = "OUTPUT ORDER"
    # RULE_ORDER = "RULE ORDER"

# class Aggregation(Enum):
    # SUM = "SUM"
    # COUNT = "COUNT"
    # MIN = "MIN"
    # MAX = "MAX"

class Decision:
    def __init__(self, id, name):
        self.id = id
        self.name = name

        self.decisionTables = []

class DecisionTable:
    def __init__(self, id, name, hit_policy):
        self.id = id
        self.name = name
        self.hit_policy = hit_policy

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
        self.row_number = 0
        self.description = ''
        self.inputEntries = []
        self.outputEntries = []


    def output_as_dict(self, task):
        script_engine = task.workflow.script_engine
        out = OrderedDict()
        for outputEntry in self.outputEntries:
            # try to use the id, but fall back to label if no name is provided.
            key = outputEntry.output.name or outputEntry.output.label
            if hasattr(outputEntry, "text") and outputEntry.text:
                outvalue = script_engine.evaluate(task, outputEntry.text)
            else:
                outvalue = ""
            if '.' in key:         # we need to allow for dot notation in the DMN -
                                   # I would use box to do this, but they didn't have a feature to build
                                   # a dict based on a dot notation withoug eval
                                   # so we build up a dictionary structure based on the key, and let the parent
                                   # do a deep merge
                currentout = {}
                subkeylist = list(reversed(key.split('.')))
                for subkey in subkeylist[:-1]:
                    currentout[subkey] = outvalue
                    outvalue = currentout
                    currentout = {}
                basekey = subkeylist[-1]
                out[basekey] = DeepMerge.merge(out.get(basekey,{}),outvalue)
            else:
                out[key] = outvalue
        return out
