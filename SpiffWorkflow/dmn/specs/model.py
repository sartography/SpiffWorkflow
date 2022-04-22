from collections import OrderedDict

from ...util.deep_merge import DeepMerge


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

    def serialize(self):
        out = {}
        out['id'] = self.id
        out['name'] = self.name
        out['inputs'] = [x.serialize() for x in self.inputs]
        out['outputs'] = [x.serialize() for x in self.outputs]
        out['rules'] = [x.serialize() for x in self.rules]
        return out

    def deserialize(self,indict):
        self.id = indict['id']
        self.name = indict['name']
        self.inputs = [Input(**x) for x in indict['inputs']]
        list(map(lambda x, y: x.deserialize(y), self.inputs, indict['inputs']))
        self.outputs = [Output(**x) for x in indict['outputs']]
        self.rules = [Rule(None) for x in indict['rules']]
        list(map(lambda x, y: x.deserialize(y),self.rules,indict['rules']))




class Input:
    def __init__(self, id, label, name, expression, typeRef):
        self.id = id
        self.label = label
        self.name = name
        self.expression = expression
        self.typeRef = typeRef

    def serialize(self):
        out = {}
        out['id'] = self.id
        out['label'] = self.label
        out['name'] = self.name
        out['expression'] = self.expression
        out['typeRef'] = self.typeRef
        return out

    def deserialize(self,indict):
        pass




class InputEntry:
    def __init__(self, id, input):
        self.id = id
        self.input = input

        self.description = ''
        self.lhs = []

    def serialize(self):
        out = {}
        out['id'] = self.id
        out['input'] = self.input.serialize()
        out['description'] = self.description
        out['lhs'] = self.lhs
        return out

    def deserialize(self, indict):
        self.id = indict['id']
        self.description = indict['description']
        self.lhs = indict['lhs']
        self.input = Input(**indict['input'])
        self.input.deserialize(indict['input'])

class Output:
    def __init__(self, id, label, name, typeRef):
        self.id = id
        self.label = label
        self.name = name
        self.typeRef = typeRef

    def serialize(self):
        out = {}
        out['id'] = self.id
        out['label'] = self.label
        out['name'] = self.name
        out['typeRef'] = self.typeRef
        return out


class OutputEntry:
    def __init__(self, id, output):
        self.id = id
        self.output = output

        self.description = ''
        self.text = ''

    def serialize(self):
        out = {}
        out['id'] = self.id
        out['output'] = self.output.serialize()
        out['description'] = self.description
        out['text'] = self.text
        return out

    def deserialize(self, indict):
        self.id = indict['id']
        self.description = indict['description']
        self.text = indict['text']
        self.output = Output(**indict['output'])



class Rule:
    def __init__(self, id):
        self.id = id

        self.description = ''
        self.inputEntries = []
        self.outputEntries = []

    def serialize(self):
        out = {}
        out['id'] = self.id
        out['description'] = self.description
        out['inputEntries'] = [x.serialize() for x in self.inputEntries]
        out['outputEntries'] = [x.serialize() for x in self.outputEntries]
        return out

    def deserialize(self,indict):
        self.id = indict['id']
        self.description = indict['description']
        self.inputEntries = [InputEntry(None,None) for x in indict['inputEntries']]
        list(map(lambda x,y : x.deserialize(y), self.inputEntries, indict['inputEntries']))
        self.outputEntries = [OutputEntry(None, None) for x in indict['outputEntries']]
        list(map(lambda x, y: x.deserialize(y), self.outputEntries, indict['outputEntries']))

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
