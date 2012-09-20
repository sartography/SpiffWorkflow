from SpiffWorkflow.operators import Operator

__author__ = 'matth'

class BpmnScriptEngine(object):

    def evaluate(self, task, expression):
        if isinstance(expression, Operator):
            return expression._matches(task)
        else:
            return self._eval(task, expression, **task.get_attributes())

    def _eval(self, task, expression, **kwargs):
        locals().update(kwargs)
        return eval(expression)

    def execute(self, task, script):
        exec script