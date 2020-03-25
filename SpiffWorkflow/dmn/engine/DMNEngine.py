import logging

from decimal import Decimal
import datetime

class DMNEngine:
    """
    Handles the processing of a decision table.
    """


    def __init__(self, decisionTable, debug=None):
        self.decisionTable = decisionTable
        self.debug = debug

        self.logger = logging.getLogger('DMNEngine')
        if not self.logger.handlers:
            self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(getattr(logging, 'DEBUG' if debug else 'INFO'))

    def decide(self, *inputArgs, **inputKwargs):
        for rule in self.decisionTable.rules:
            self.logger.debug('Checking rule %s (%s)...' % (rule.id, rule.description))

            res = self.__checkRule(rule, *inputArgs, **inputKwargs)
            self.logger.debug(' Match? %s' % (res))
            if res:
                self.logger.debug(' Return %s (%s)' % (rule.id, rule.description))
                return rule

    def __checkRule(self, rule, *inputData, **inputKwargs):
        for idx, inputEntry in enumerate(rule.inputEntries):
            input = self.decisionTable.inputs[idx]

            self.logger.debug(' Checking input entry %s (%s: %s)...' % (inputEntry.id, input.label, inputEntry.operators))

            for operator, parsedValue in inputEntry.operators:
                if parsedValue is not None:
                    inputVal = DMNEngine.__getInputVal(inputEntry, idx, *inputData, **inputKwargs)
                    if isinstance(parsedValue, Decimal) and not isinstance(inputVal, Decimal):
                        self.logger.warning('Attention, you are comparing a Decimal with %r' % (type(inputVal)))

                    if operator == 'in' or operator == 'not in':
                        expression = '%r %s %r' % (parsedValue,  operator, inputVal)
                    else:
                        expression = '%r %s %r' % (inputVal, operator, parsedValue)

                    self.logger.debug(' Evaludation expression: %s' % (expression))
                    if not eval(expression):
                        return False  # Value does not match
                    else:
                        continue  # Check the other operators/columns
                else:
                    # Empty means ignore decision value
                    self.logger.debug(' Value not defined')
                    continue  # Check the other operators/columns

        self.logger.debug(' All inputs checked')
        return True

    @staticmethod
    def __getInputVal(inputEntry, idx, *inputData, **inputKwargs):
        """
        The input of the decision method can be args or kwargs.
        This function tries to extract the input data from args if passed,
         otherwise from kwargs using the label of the decision input column as mapping

        :param inputEntry:
        :param idx:
        :param inputData:
        :param inputKwargs:
        :return:
        """

        return inputData[idx] if inputData else inputKwargs[inputEntry.input.label] # TODO: label?
