from ...bpmn.serializer.bpmn_converters import BpmnDataConverter, BpmnTaskSpecConverter

from ..specs.BusinessRuleTask import BusinessRuleTask
from ..specs.model import Decision, DecisionTable, Rule
from ..specs.model import Input, InputEntry, Output, OutputEntry
from ..engine.DMNEngine import DMNEngine

class BusinessRuleTaskConverter(BpmnTaskSpecConverter):

    def __init__(self, data_converter=None, typename=None):
        super().__init__(BusinessRuleTask, data_converter, typename)

    def to_dict(self, spec):
        dct = self.get_default_attributes(spec)
        dct.update(self.get_bpmn_attributes(spec))
        # We only ever use one decision table
        dct['decision_table'] = self.decision_table_to_dict(spec.dmnEngine.decisionTable)
        return dct

    def decision_table_to_dict(self, table):
        return {
            'id': table.id,
            'name': table.name,
            'inputs': [val.__dict__ for val in table.inputs],
            'outputs': [val.__dict__ for val in table.outputs],
            'rules': [self.rule_to_dict(rule) for rule in table.rules],
        }

    def input_entry_to_dict(self, entry):
        return {
            'id': entry.id,
            'input': entry.input.__dict__,
            'description': entry.description,
            'lhs': entry.lhs,
        }

    def output_entry_to_dict(self, entry):
        dct = {
            'id': entry.id,
            'output': entry.output.__dict__,
            'description': entry.description,
            'text': entry.text,
        }
        # Why do we have attributes that aren't defined in __init__??
        if hasattr(entry, 'parsedRef'):
            dct['parsed_ref'] = entry.parsedRef
        return dct

    def rule_to_dict(self, rule):
        return {
            'id': rule.id,
            'description': rule.description,
            'input_entries': [self.input_entry_to_dict(entry) for entry in rule.inputEntries],
            'output_entries': [self.output_entry_to_dict(entry) for entry in rule.outputEntries],
        }

    def from_dict(self, dct):
        table = self.decision_table_from_dict(dct.pop('decision_table'))
        dct['dmnEngine'] = DMNEngine(table)
        return self.task_spec_from_dict(dct)

    def decision_table_from_dict(self, dct):
        table = DecisionTable(dct['id'], dct['name'])
        table.inputs = [ Input(**val) for val in dct['inputs'] ]    
        table.outputs = [ Output(**val) for val in dct['outputs'] ]
        table.rules = [ self.rule_from_dict(rule) for rule in dct['rules'] ]
        return table

    def input_entry_from_dict(self, dct):
        val = Input(**dct.pop('input'))
        entry = InputEntry(dct['id'], val)
        entry.description = dct['description']
        entry.lhs = dct['lhs']
        return entry

    def output_entry_from_dict(self, dct):
        val = Output(**dct.pop('output'))
        entry = OutputEntry(dct['id'], val)
        entry.description = dct['description']
        entry.text = dct['text']
        if 'parsed_ref' in dct:
            entry.parsedRef = dct['parsed_ref']
        return entry

    def rule_from_dict(self, dct):
        rule = Rule(dct['id'])
        rule.description = dct['description']
        rule.inputEntries = [ self.input_entry_from_dict(entry) for entry in dct['input_entries'] ]
        rule.outputEntries = [ self.output_entry_from_dict(entry) for entry in dct['output_entries'] ]
        return rule