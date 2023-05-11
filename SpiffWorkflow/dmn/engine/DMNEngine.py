# Copyright (C) 2023 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

import logging
import re

from SpiffWorkflow.exceptions import SpiffWorkflowException
from SpiffWorkflow.bpmn.exceptions import WorkflowTaskException

from ..specs.model import HitPolicy

logger = logging.getLogger('spiff.dmn')


class DMNEngine:
    """
    Handles the processing of a decision table.
    """

    def __init__(self, decision_table):
        self.decision_table = decision_table

    def decide(self, task):
        rules = []
        for rule in self.decision_table.rules:
            if self.__check_rule(rule, task):
                rules.append(rule)
                if self.decision_table.hit_policy == HitPolicy.UNIQUE.value:
                    return rules
        return rules

    def result(self, task):
        """Returns the results of running this decision table against
        a given task."""
        result = {}
        matched_rules = self.decide(task)
        if self.decision_table.hit_policy == HitPolicy.COLLECT.value:
            # each output will be an array of values, all outputs will
            # be placed in a dict, which we will then merge.
            for rule in matched_rules:
                rule_output = rule.output_as_dict(task)
                for key in rule_output.keys():
                    if not key in result:
                        result[key] = []
                    result[key].append(rule_output[key])
        elif len(matched_rules) > 0:
            result = matched_rules[0].output_as_dict(task)
        return result


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
                except SpiffWorkflowException as se:
                    se.add_note(f"Rule failed on row {rule.row_number}")
                    raise se
                except Exception as e:
                    error = WorkflowTaskException(str(e), task=task, exception=e)
                    error.add_note(f"Failed to execute DMN Rule on row {rule.row_number}")
                    raise error
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
        script_engine.validate(input_expr)

        # If we get here, we need to check whether the match expression includes
        # an operator or if can use '=='
        needs_eq = self.needs_eq(script_engine, match_expr)
        # Disambiguate cases like a == 0 == True when we add '=='
        expr = f'({input_expr}) == ({match_expr})' if needs_eq else input_expr + match_expr
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
