from SpiffWorkflow.operators import Operator

__author__ = 'matth'

class BpmnScriptEngine(object):
    """
    Used during execution of a BPMN workflow to evaluate condition / value expressions. These are used by
    Gateways, and by Catching Events (non-message ones).

    Also used to execute scripts.

    If you are uncomfortable with the use of eval() and exec, then you should provide a specialised
    subclass that parses and executes the scripts / expressions in a mini-language of your own.
    """

    def evaluate(self, task, expression):
        """
        Evaluate the given expression, within the context of the given task and return the result.
        """
        if isinstance(expression, Operator):
            return expression._matches(task)
        else:
            return self._eval(task, expression, **task.get_attributes())

    def execute(self, task, script):
        """
        Execute the script, within the context of the specified task
        """
        exec script

    def _eval(self, task, expression, **kwargs):
        locals().update(kwargs)
        return eval(expression)

