import ast

from SpiffWorkflow.bpmn.parser.node_parser import NodeParser, DEFAULT_NSMAP
from ...bpmn.parser.ValidationException import ValidationException

from ...bpmn.parser.util import xpath_eval

from ...dmn.specs.model import Decision, DecisionTable, InputEntry, \
    OutputEntry, Input, Output, Rule

def get_dmn_ns(node):
    """
    Returns the namespace definition for the current DMN

    :param node: the XML node for the DMN document
    """
    nsmap = DEFAULT_NSMAP.copy()
    if 'http://www.omg.org/spec/DMN/20151101/dmn.xsd' in node.nsmap.values():
        nsmap['dmn'] = 'http://www.omg.org/spec/DMN/20151101/dmn.xsd'
    elif 'http://www.omg.org/spec/DMN/20180521/DI/' in node.nsmap.values():
        nsmap['dmn'] = 'http://www.omg.org/spec/DMN/20180521/DI/'
    elif 'https://www.omg.org/spec/DMN/20191111/MODEL/' in node.nsmap.values():
        nsmap['dmn'] = 'https://www.omg.org/spec/DMN/20191111/MODEL/'
    return nsmap

class DMNParser(NodeParser):
    """
    Please note this DMN Parser still needs a lot of work.  A few key areas
    that need to be addressed:
    1. it assumes that only one decision table exists within a decision
    2. it is not always name space aware (I fixed the top level, but could be
       cleaner all the way through.
    """

    DT_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, p, node, nsmap, svg=None, filename=None):
        """
        Constructor.

        :param p: the owning BpmnParser instance
        :param node: the XML node for the DMN document
        :param svg: the SVG representation of this process as a string
          (optional)
        :param filename: the source BMN filename (optional)
        """
        super().__init__(node, nsmap, filename=filename)

        self.parser = p
        self.node = node
        self.decision = None
        self.svg = svg
        self.filename = filename

    def parse(self):
        self.decision = self._parse_decision(self.node.findall('{*}decision'))

    def get_id(self):
        """
        Returns the process ID
        """
        return self.node.findall('{*}decision[1]')[0].get('id')

    def get_name(self):
        """
        Returns the process name (or ID, if no name is included in the file)
        """
        return self.node.findall('{*}decision[1]')[0].get('name')

    def _parse_decision(self, root):
        decision_elements = list(root)
        if len(decision_elements) == 0:
            raise ValidationException('No decisions found', file_name=self.filename,
                                      node=root)

        if len(decision_elements) > 1:
            raise ValidationException('Multiple decision tables are not current supported.',
                                      file_name=self.filename, node=root)

        decision_element = decision_elements[0]

        decision = Decision(decision_element.attrib['id'],
                            decision_element.attrib.get('name', ''))

        # Parse decision tables
        self._parse_decision_tables(decision, decision_element)

        return decision

    def _parse_decision_tables(self, decision, decisionElement):
        for decision_table_element in decisionElement.findall('{*}decisionTable'):
            name = decision_table_element.attrib.get('name', '')
            hitPolicy = decision_table_element.attrib.get('hitPolicy', 'UNIQUE').upper()
            decision_table = DecisionTable(decision_table_element.attrib['id'],
                                           name, hitPolicy)
            decision.decisionTables.append(decision_table)

            # parse inputs
            self._parse_inputs_outputs(decision_table, decision_table_element)

    def _parse_inputs_outputs(self, decisionTable,
                              decisionTableElement):
        rule_counter = 0
        for element in decisionTableElement:
            if element.tag.endswith('input'):
                e_input = self._parse_input(element)
                decisionTable.inputs.append(e_input)
            elif element.tag.endswith('output'):
                output = self._parse_output(element)
                decisionTable.outputs.append(output)
            elif element.tag.endswith('rule'):
                rule_counter += 1
                rule = self._parse_rule(decisionTable, element, rule_counter)
                decisionTable.rules.append(rule)
            else:
                raise ValidationException(
                    'Unknown type in decision table: %r' % element.tag,
                    node=element, file_name=self.filename)

    def _parse_input(self, input_element):
        type_ref = None
        prefix = self.nsmap['dmn']
        xpath = xpath_eval(input_element, {'dmn': prefix})
        expression = None
        for input_expression in xpath('dmn:inputExpression'):
            type_ref = input_expression.attrib.get('typeRef', '')
            expression_node = input_expression.find('{' + prefix + '}text')
            if expression_node is not None:
                expression = expression_node.text

        return Input(input_element.attrib['id'],
                     input_element.attrib.get('label', ''),
                     input_element.attrib.get('name', ''),
                     expression,
                     type_ref)

    def _parse_output(self, outputElement):
        output = Output(outputElement.attrib['id'],
                        outputElement.attrib.get('label', ''),
                        outputElement.attrib.get('name', ''),
                        outputElement.attrib.get('typeRef', ''))
        return output

    def _parse_rule(self, decisionTable, ruleElement, rowNumber):
        rule = Rule(ruleElement.attrib['id'])
        rule.row_number = rowNumber
        input_idx = 0
        output_idx = 0
        for child in ruleElement:
            # Load description
            if child.tag.endswith('description'):
                rule.description = child.text

            # Load input entries
            elif child.tag.endswith('inputEntry'):
                input_entry = self._parse_input_output_element(decisionTable,
                                                               child,
                                                               InputEntry,
                                                               input_idx)
                rule.inputEntries.append(input_entry)
                input_idx += 1

            # Load output entries
            elif child.tag.endswith('outputEntry'):
                output_entry = self._parse_input_output_element(decisionTable,
                                                                child,
                                                                OutputEntry,
                                                                output_idx)
                rule.outputEntries.append(output_entry)
                output_idx += 1

        return rule

    def _parse_input_output_element(self, decision_table, element, cls, idx):
        input_or_output = (
            decision_table.inputs if cls == InputEntry else decision_table.outputs if cls == OutputEntry else None)[
            idx]
        entry = cls(element.attrib['id'], input_or_output)
        for child in element:
            if child.tag.endswith('description'):
                entry.description = child.text
            elif child.tag.endswith('text'):
                entry.text = child.text
        if cls == InputEntry:
            entry.lhs.append(entry.text)
        elif cls == OutputEntry:
            if entry.text and entry.text != '':
                try:
                    ast.parse(entry.text)
                except Exception as e:
                    raise ValidationException(
                        "Malformed Output Expression '%s'. %s " % (entry.text, str(e)),
                        node=element, file_name=self.filename)
        return entry
