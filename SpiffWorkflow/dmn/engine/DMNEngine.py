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

    def decide(self, script_engine, task, context):
        for rule in self.decisionTable.rules:
            res = self.__checkRule(rule, script_engine, task, context)
            if res:
                return rule

    def __checkRule(self, rule, script_engine, task, context):
        for idx, inputEntry in enumerate(rule.inputEntries):
            input = self.decisionTable.inputs[idx]
            local_data = {}
            if context and isinstance(context, dict):
                local_data.update(context)

            for lhs in inputEntry.lhs:
                if lhs is not None:
                    input_val = DMNEngine.__getInputVal(inputEntry, context)
                else:
                    input_val = None
                try:
                    if not script_engine.eval_dmn_expression(input_val, lhs,
                                                             context, task):
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
                                        input_val, lhs, rule.description, str(e),str(most_similar)))
                except Exception as e:
                    raise Exception("Failed to execute "
                                    "expression: '%s' is '%s' in the "
                                    "Row with annotation '%s', %s" % (
                                        input_val, lhs, rule.description, str(e)))
                else:
                    # Empty means ignore decision value
                    continue  # Check the other operators/columns
        return True

    @staticmethod
    def __getInputVal(inputEntry, context):
        """
        The input of the decision method should be an expression,  but will
        fallback to the likely very bad idea of trying to use the label.

        :param inputEntry:
        :param context:  # A dictionary that provides some context/local vars.
        :return:
        """
        if inputEntry.input.expression:
            return inputEntry.input.expression
        else:
            # Backwards compatibility
            return "%r" % context[inputEntry.input.label]
