import logging
import re

from ...util import levenshtein
from ...workflow import WorkflowException

logger = logging.getLogger('spiff.dmn')


class DMNEngine:
    """
    Handles the processing of a decision table.
    """

    def __init__(self, decision_table):
        self.decision_table = decision_table

    def decide(self, task):
        for rule in self.decision_table.rules:
            if self.__check_rule(rule, task):
                return rule

    def __check_rule(self, rule, task):
        for input_entry in rule.inputEntries:
            for lhs in input_entry.lhs:
                if lhs is not None:
                    input_val = DMNEngine.__get_input_val(input_entry, task.data)
                else:
                    input_val = None
                try:
                    if not self.evaluate(input_val, lhs, task):
                        return False
                except NameError as e:
                    # Add a bit of info, re-raise as Name Error
                    raise NameError(str(e) + "Failed to execute "
                                    "expression: '%s' is '%s' in the "
                                    "Row with annotation '%s'")
                except WorkflowException as we:
                    raise we
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

    def evaluate(self, input_expr, match_expr, task):
        """
        Here we need to handle a few things such as if it is an equality or if
        the equality has already been taken care of. For now, we just assume
         it is equality.

         An optional task can be included if this is being executed in the
         context of a BPMN task.
        """
        if match_expr is None:
            return True

        script_engine = task.workflow.script_engine
        # NB - the question mark allows us to do a double ended test - for
        # example - our input expr is 5 and the match expr is 4 < ? < 6  -
        # this should evaluate as 4  < 5 < 6 and it should evaluate as 'True'
        # NOTE:  It should only do this replacement outside of quotes.
        # for example, provided "This thing?"  in quotes, it should not
        # do the replacement.
        match_expr = re.sub('(\?)(?=(?:[^\'"]|[\'"][^\'"]*[\'"])*$)', 'dmninputexpr', match_expr)
        if 'dmninputexpr' in match_expr:
            external_methods = {
                'dmninputexpr': script_engine.evaluate(task, input_expr)
            }
            return script_engine.evaluate(task, match_expr,
                                          external_methods=external_methods)

        # The input expression just has to be something that can be parsed as is by the engine.
        try:
            script_engine.validate(input_expr)
        except Exception as e:
            raise WorkflowException(f"Input Expression '{input_expr}' is malformed. " + str(e))

        # If we get here, we need to check whether the match expression includes
        # an operator or if can use '=='
        needs_eq = self.needs_eq(script_engine, match_expr)
        expr = input_expr + ' == ' + match_expr if needs_eq else input_expr + match_expr
        return script_engine.evaluate(task, expr)

    @staticmethod
    def __get_input_val(input_entry, context):
        """
        The input of the decision method should be an expression,  but will
        fallback to the likely very bad idea of trying to use the label.

        :param inputEntry:
        :param context:  # A dictionary that provides some context/local vars.
        :return:
        """
        if input_entry.input.expression:
            return input_entry.input.expression
        else:
            # Backwards compatibility
            return "%r" % context[input_entry.input.label]
