import ast

from ...bpmn.parser.util import xpath_eval

from ...dmn.specs.model import Decision, DecisionTable, InputEntry, \
    OutputEntry, Input, Output, Rule


def get_dmn_ns(node):
    """
    Returns the namespace definition for the current DMN

    :param node: the XML node for the DMN document
    """
    if 'http://www.omg.org/spec/DMN/20151101/dmn.xsd' in node.nsmap.values():
        return 'http://www.omg.org/spec/DMN/20151101/dmn.xsd'
    elif 'https://www.omg.org/spec/DMN/20191111/MODEL/' in node.nsmap.values():
        return 'https://www.omg.org/spec/DMN/20191111/MODEL/'
    return None


class DMNParser(object):
    """
    Please note this DMN Parser still needs a lot of work.  A few key areas
    that need to be addressed:
    1. it assumes that only one decision table exists within a decision
    2. it is not always name space aware (I fixed the top level, but could be
       cleaner all the way through.
    """

    DT_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, p, node, svg=None, filename=None, doc_xpath=None):
        """
        Constructor.

        :param p: the owning BpmnParser instance
        :param node: the XML node for the DMN document
        :param svg: the SVG representation of this process as a string
          (optional)
        :param filename: the source BMN filename (optional)
        """
        self.parser = p
        self.node = node
        self.decision = None
        self.svg = svg
        self.filename = filename
        self.doc_xpath = doc_xpath
        self.dmn_ns = get_dmn_ns(self.node)
        self.xpath = xpath_eval(self.node, {'dmn': self.dmn_ns})

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
            raise Exception('No decisions found')

        if len(decision_elements) > 1:
            raise Exception('Multiple decisions found')

        decision_element = decision_elements[0]
        assert decision_element.tag.endswith(
            'decision'), 'Element %r is not of type "decision"' % (
            decision_element.tag)

        decision = Decision(decision_element.attrib['id'],
                            decision_element.attrib.get('name', ''))

        # Parse decision tables
        try:
            self._parse_decision_tables(decision, decision_element)
        except Exception as e:
            raise Exception(
                "Error in Decision '%s': %s" % (decision.name, str(e)))

        return decision

    def _parse_decision_tables(self, decision, decisionElement):
        for decision_table_element in decisionElement.findall('{*}decisionTable'):
            decision_table = DecisionTable(decision_table_element.attrib['id'],
                                           decision_table_element.attrib.get(
                                               'name', ''))
            decision.decisionTables.append(decision_table)

            # parse inputs
            self._parse_inputs_outputs(decision_table, decision_table_element)

    def _parse_inputs_outputs(self, decisionTable,
                              decisionTableElement):
        for element in decisionTableElement:
            if element.tag.endswith('input'):
                e_input = self._parse_input(element)
                decisionTable.inputs.append(e_input)
            elif element.tag.endswith('output'):
                output = self._parse_output(element)
                decisionTable.outputs.append(output)
            elif element.tag.endswith('rule'):
                rule = self._parse_rule(decisionTable, element)
                decisionTable.rules.append(rule)
            else:
                raise Exception(
                    'Unknown type in decision table: %r' % element.tag)

    def _parse_input(self, input_element):
        type_ref = None
        xpath = xpath_eval(input_element, {'dmn': self.dmn_ns})
        expression = None
        for input_expression in xpath('dmn:inputExpression'):
            type_ref = input_expression.attrib.get('typeRef', '')
            expression_node = input_expression.find('{' + self.dmn_ns + '}text')
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

    def _parse_rule(self, decisionTable, ruleElement):
        rule = Rule(ruleElement.attrib['id'])

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
                    raise Exception(
                        "Malformed Output Expression '%s'. %s " % (entry.text, str(e)))
        return entry
