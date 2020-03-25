import re
from decimal import Decimal
from ast import literal_eval
from xml.etree import ElementTree
from datetime import datetime

from SpiffWorkflow.bpmn.parser.util import xpath_eval

from SpiffWorkflow.dmn.specs.model import Decision, DecisionTable, InputEntry, \
    OutputEntry, Input, Output, Rule

DMN_NS = 'http://www.omg.org/spec/DMN/20151101/dmn.xsd'

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
        self.xpath = xpath_eval(self.node, {'dmn': DMN_NS})

    def parse(self):
        self.decision = DMNParser.__parse_decision(self.node)

    def get_id(self):
        """
        Returns the process ID
        """
        return self.xpath('dmn:decision[1]')[0].get('id')

    def get_name(self):
        """
        Returns the process name (or ID, if no name is included in the file)
        """
        return self.xpath('dmn:decision[1]')[0].get('name')



    @staticmethod
    def __parse_decision(root):
        decisionElements = list(root)
        if len(decisionElements) == 0:
            raise Exception('No decisions found')

        if len(decisionElements) > 1:
            raise Exception('Multiple decisions found')

        decisionElement = decisionElements[0]
        assert decisionElement.tag.endswith(
            'decision'), 'Element %r is not of type "decision"' % (
            decisionElement.tag)

        decision = Decision(decisionElement.attrib['id'],
                            decisionElement.attrib.get('name', ''))

        # Parse decision tables
        DMNParser.__parseDecisionTables(decision, decisionElement)

        return decision

    @staticmethod
    def __parseDecisionTables(decision, decisionElement):
        xpath = xpath_eval(decisionElement, {'dmn': DMN_NS})
        for decisionTableElement in xpath('dmn:decisionTable'):
            decisionTable = DecisionTable(decisionTableElement.attrib['id'],
                                          decisionTableElement.attrib.get(
                                              'name', ''))
            decision.decisionTables.append(decisionTable)

            # parse inputs
            DMNParser.__parseInputsOutputs(decision, decisionTable,
                                           decisionTableElement)

    @staticmethod
    def __parseInputsOutputs(decision, decisionTable, decisionTableElement):
        for element in decisionTableElement:
            if element.tag.endswith('input'):
                input = DMNParser.__parseInput(element)
                decisionTable.inputs.append(input)
            elif element.tag.endswith('output'):
                output = DMNParser.__parseOutput(element)
                decisionTable.outputs.append(output)
            elif element.tag.endswith('rule'):
                rule = DMNParser.__parseRule(decision, decisionTable, element)
                decisionTable.rules.append(rule)
            else:
                raise Exception(
                    'Unknown type in decision table: %r' % (element.tag))

    @staticmethod
    def __parseInput(inputElement):
        typeRef = None
        for inputExpression in inputElement:
            assert inputExpression.tag.endswith(
                'inputExpression'), 'Element %r is not of type "inputExpression"' % (
                inputExpression.tag)

            typeRef = inputExpression.attrib.get('typeRef', '')

        input = Input(inputElement.attrib['id'],
                      inputElement.attrib.get('label', ''),
                      inputElement.attrib.get('name', ''), typeRef)
        return input

    @staticmethod
    def __parseOutput(outputElement):
        output = Output(outputElement.attrib['id'],
                        outputElement.attrib.get('label', ''),
                        outputElement.attrib.get('name', ''),
                        outputElement.attrib.get('typeRef', ''))
        return output

    @staticmethod
    def __parseRule(decision, decisionTable, ruleElement):
        rule = Rule(ruleElement.attrib['id'])

        inputIdx = 0
        outputIdx = 0
        for child in ruleElement:
            # Load description
            if child.tag.endswith('description'):
                rule.description = child.text

            # Load input entries
            elif child.tag.endswith('inputEntry'):
                inputEntry = DMNParser.__parseInputOutputElement(decision,
                                                                 decisionTable,
                                                                 child,
                                                                 InputEntry,
                                                                 inputIdx)
                rule.inputEntries.append(inputEntry)
                inputIdx += 1

            # Load output entries
            elif child.tag.endswith('outputEntry'):
                outputEntry = DMNParser.__parseInputOutputElement(decision,
                                                                  decisionTable,
                                                                  child,
                                                                  OutputEntry,
                                                                  outputIdx)
                rule.outputEntries.append(outputEntry)
                outputIdx += 1

        return rule

    @staticmethod
    def __parseInputOutputElement(decision, decisionTable, element, cls, idx):
        inputOrOutput = (
            decisionTable.inputs if cls == InputEntry else decisionTable.outputs if cls == OutputEntry else None)[
            idx]
        entry = cls(element.attrib['id'], inputOrOutput)

        for child in element:
            if child.tag.endswith('description'):
                entry.description = child.text
            elif child.tag.endswith('text'):
                entry.text = child.text

                if cls == InputEntry:
                    entry.operators = list(
                        DMNParser.__parseRef(inputOrOutput.typeRef,
                                             entry.text))
                elif cls == OutputEntry:
                    operators = list(
                        DMNParser.__parseRef(inputOrOutput.typeRef,
                                             entry.text))
                    assert len(
                        operators) <= 1, 'Normally it is impossible to have multiple values as output column! %s: %r' % (
                    inputOrOutput.typeRef, entry.text)
                    entry.parsedValue = operators[0][1]
                else:
                    raise NotImplementedError(cls.__name__)

        return entry

    @staticmethod
    def __parseRef(typeRef, val):
        if val is None:
            return []

        if typeRef == 'string':
            return DMNParser.__parseString(val)

        elif typeRef == 'boolean':
            return DMNParser.__parseBoolean(val)

        elif typeRef == 'integer':
            return DMNParser.__parseInteger(val)

        elif typeRef in ('long', 'double'):
            return DMNParser.__parseLongOrDouble(val)

        elif typeRef == 'date':
            return DMNParser.__parseDate(val)

        else:
            raise NotImplementedError(typeRef)

    @staticmethod
    def __parseString(val):
        """This could be worse.  But I'm not longer wholly ashamed of it."""
        val = val.strip()
        match_not_contains = re.match("^not contains\((.+)\)$", val)
        match_contains = re.match("contains\((.+)\)", val)
        match_not = re.match("not\((.+)\)", val)
        if match_not:
            val = match_not.group(1)
            expression = "!="
        elif match_contains:
            val = match_contains.group(1)
            expression = "in"
        elif match_not_contains:
            val = match_not_contains.group(1)
            expression = "not in"
        else:
            expression = "=="
        return [(expression, literal_eval(val))]

    @staticmethod
    def __parseBoolean(val):
        return [('==', {'true': True, 'false': False}.get(val, None))]

    @staticmethod
    def __parseInteger(val):
        if '..' in val:
            intStrFrm, intStrTo = val[1:-1].split('..')
            return [
                ('>=' if val[0] == '[' else '>', int(intStrFrm)),
                ('<=' if val[-1] == ']' else '<', int(intStrTo))
            ]
        elif val.startswith(('<', '>', '=')):
            vals = val.split(' ')
            return [(vals[0], int(vals[1]))]
        else:
            return [('==', int(val))]

    @staticmethod
    def __parseLongOrDouble(val):
        if '..' in val:
            intStrFrm, intStrTo = val[1:-1].split('..')
            return [
                ('>=' if val[0] == '[' else '>', Decimal(intStrFrm)),
                ('<=' if val[-1] == ']' else '<', Decimal(intStrTo))
            ]
        elif val.startswith(('<', '>', '=')):
            vals = val.split(' ')
            return [(vals[0], Decimal(vals[1]))]
        else:
            return [('==', Decimal(val))]

    @staticmethod
    def __parseDate(val):
        if '..' in val:
            # Example: [date and time("2017-11-03T00:00:00")..date and time("2017-11-04T23:59:59")]
            dtStrFrm, dtStrTo = val[1:-1].split('..')
            dtFrm = DMNParser.__parseDateStr(dtStrFrm)
            dtTo = DMNParser.__parseDateStr(dtStrTo)
            return [
                ('>=' if val[0] == '[' else '>', dtFrm),
                ('<=' if val[-1] == ']' else '<', dtTo)
            ]
        elif val.startswith(('>', '<')):
            # Example: > date and time("2017-11-03T00:00:00")
            # Example: < date and time("2017-11-03T00:00:00")
            operator, dtStr = val.split(' ', 1)
            dt = DMNParser.__parseDateStr(dtStr)
            return [(operator, dt)]
        else:
            return [('==', DMNParser.__parseDateStr(val))]

    @staticmethod
    def __parseDateStr(val):
        # Example: date and time("2017-11-03T00:00:00")
        dtStrVal = val.replace('date and time("', '').replace('")', '')
        return datetime.strptime(dtStrVal, DMNParser.DT_FORMAT)
