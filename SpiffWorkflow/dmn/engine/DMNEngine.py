import logging
import re

from ...util import levenshtein
from ...workflow import WorkflowException


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
            if self.__checkRule(rule, script_engine, task, context):
                return rule

    def __checkRule(self, rule, script_engine, task, context):
        for input_entry in rule.inputEntries:
            local_data = {}
            if context and isinstance(context, dict):
                local_data.update(context)

            for lhs in input_entry.lhs:
                if lhs is not None:
                    input_val = DMNEngine.__getInputVal(input_entry, context)
                else:
                    input_val = None
                try:
                    if not self.evaluate(script_engine, input_val, lhs, context, task):
                        return False
                except NameError as e:
                    bad_variable = re.match("name '(.+)' is not defined", str(e)).group(1)
                    most_similar = levenshtein.most_similar(bad_variable, local_data.keys(), 3)
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

    def needs_eq(self, script_engine, text):
        try:
            # this should work if we can just do a straight equality
            script_engine.validate(text)
            return True
        except SyntaxError:
            # if we have problems parsing, then we introduce a variable on the left hand side 
            # and try that and see if that parses. If so, then we know that we do not need to 
            # introduce an equality operator later in the dmn
            script_engine.validate(f'v {text}')
            return False

    def evaluate(self, script_engine, input_expr, match_expr, context, task=None):
        """
        Here we need to handle a few things such as if it is an equality or if
        the equality has already been taken care of. For now, we just assume
         it is equality.

         An optional task can be included if this is being executed in the
         context of a BPMN task.
        """
        if match_expr is None:
            return True

        # NB - the question mark allows us to do a double ended test - for
        # example - our input expr is 5 and the match expr is 4 < ? < 6  -
        # this should evaluate as 4  < 5 < 6 and it should evaluate as 'True'
        # NOTE:  It should only do this replacement outside of quotes.
        # for example, provided "This thing?"  in quotes, it should not
        # do the replacement.
        match_expr = re.sub('(\?)(?=(?:[^\'"]|[\'"][^\'"]*[\'"])*$)', 'dmninputexpr', match_expr)
        if 'dmninputexpr' in match_expr:
            external_methods = {
                'dmninputexpr': script_engine._evaluate(input_expr, context, task)
            }
            return script_engine._evaluate(match_expr, context, task, external_methods)

        # The input expression just has to be something that can be parsed as is by the engine.
        try:
            script_engine.validate(input_expr)
        except:
            raise WorkflowException(f"Input Expression '{input_expr}' is malformed")

        # If we get here, we need to check whether the match expression includes
        # an operator or if can use '=='
        needs_eq = self.needs_eq(script_engine, match_expr)
        expr = input_expr + ' == ' + match_expr if needs_eq else input_expr + match_expr
        return script_engine._evaluate(expr, context, task)

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
