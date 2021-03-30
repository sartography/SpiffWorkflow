import logging
import Levenshtein
import re
from SpiffWorkflow.bpmn.DMNPythonScriptEngine import DMNPythonScriptEngine


class DMNEngine:
    """
    Handles the processing of a decision table.
    """


    def __init__(self, decisionTable, debug=None):
        self.decisionTable = decisionTable
        self.debug = debug
        self.scriptEngine = DMNPythonScriptEngine()
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

            self.logger.debug(' Checking input entry %s (%s: %s)...' % (inputEntry.id, input.label, inputEntry.lhs))
            # if inputData:
            #     self.logger.debug('inputData:', inputData)
            # if inputKwargs:
            #     self.logger.debug('inputKwargs:', inputKwargs)
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
                    #PythonScriptEngine.convertToBox(DMNPythonScriptEngine(),local_data)
                    if not input.scriptEngine.eval_dmn_expression(inputVal, lhs, **local_data):
                        return False
                except NameError as e:
                    x = re.match("name '(.+)' is not defined",str(e))
                    name = x.group(1)
                    distances = [(key,Levenshtein.distance(name,key)) for key in local_data.keys()]
                    distances.sort(key=lambda x: x[1])

                    raise NameError("Failed to execute "
                                    "expression: '%s' is '%s' in the "
                                    "Row with annotation '%s'.  The following "
                                    "value does not exist: %s - did you mean one of %s?" % (
                                        inputVal, lhs, rule.description, str(e),str([x[0] for x in distances[:3]])))
                except Exception as e:
                    raise Exception("Failed to execute "
                                    "expression: '%s' is '%s' in the "
                                    "Row with annotation '%s', %s" % (
                                        inputVal, lhs, rule.description, str(e)))
                else:
                    # Empty means ignore decision value
                    self.logger.debug(' Value not defined')
                    continue  # Check the other operators/columns

        self.logger.debug(' All inputs checked')
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
