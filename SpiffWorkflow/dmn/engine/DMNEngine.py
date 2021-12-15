import logging
import re
from ...util import levenshtein


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

    def decide(self, script_engine, *inputArgs, **inputKwargs):
        for rule in self.decisionTable.rules:
            res = self.__checkRule(rule, script_engine, *inputArgs, **inputKwargs)
            if res:
                return rule

    def __checkRule(self, rule, script_engine, *inputData, **inputKwargs):
        for idx, inputEntry in enumerate(rule.inputEntries):
            input = self.decisionTable.inputs[idx]
            local_data = {}
            local_data.update(inputKwargs)
            if inputData and isinstance(inputData[idx], dict):
                local_data.update(inputData[idx])

            for lhs in inputEntry.lhs:
                if lhs is not None:
                    inputVal = DMNEngine.__getInputVal(inputEntry, idx, *inputData, **inputKwargs)
                else:
                    inputVal = None
                try:
                    if not script_engine.eval_dmn_expression(inputVal, lhs, **local_data):
                        return False
                except NameError as e:
                    bad_variable = re.match("name '(.+)' is not defined",
                                            str(e)).group(1)
                    most_similar = levenshtein.most_similar(bad_variable,
                                                            local_data.keys(),
                                                            3)
                    raise NameError("Failed to execute "
                                    "expression: '%s' is '%s' in the "
                                    "Row with annotation '%s'.  The following "
                                    "value does not exist: %s - did you mean one of %s?" % (
                                        inputVal, lhs, rule.description, str(e),str(most_similar)))
                except Exception as e:
                    raise Exception("Failed to execute "
                                    "expression: '%s' is '%s' in the "
                                    "Row with annotation '%s', %s" % (
                                        inputVal, lhs, rule.description, str(e)))
                else:
                    # Empty means ignore decision value
                    continue  # Check the other operators/columns
        return True

    @staticmethod
    def __getInputVal(inputEntry, idx, *inputData, **inputKwargs):
        """
        The input of the decision method can be an expression, args or kwargs.
        It prefers an input expression per the Specification, but will fallback
        to using inputData if available.  Finally it will fall back to the
        likely very bad idea of trying to use the label.

        :param inputEntry:
        :param idx:
        :param inputData:
        :param inputKwargs:
        :return:
        """
        if inputEntry.input.expression:
            return inputEntry.input.expression
        elif inputData:
            return "%r" % inputData[idx]
        else:
            # Backwards compatibility
            return "%r" % inputKwargs[inputEntry.input.label]
