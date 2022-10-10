import re

from SpiffWorkflow.exceptions import WorkflowException, WorkflowTaskException
from SpiffWorkflow.util import levenshtein

class WorkflowTaskExecException(WorkflowTaskException):
    """
    Exception during execution of task "payload". For example:

    * ScriptTask during execution of embedded script,
    * ServiceTask during external service call.
    """

    def __init__(self, task, error_msg, exception=None, line_number=0, error_line=""):
        """
        Exception initialization.

        :param task: the task that threw the exception
        :type task: Task
        :param exception: a human readable error message
        :type exception: Exception

        """

        self.offset = 0
        self.line_number = line_number
        self.error_line = error_line

        if isinstance(exception, SyntaxError):
            # Prefer line number from syntax error if available.
            self.line_number = exception.lineno
            self.offset = exception.offset
        elif isinstance(exception, NameError):
            def_match = re.match("name '(.+)' is not defined", str(exception))
            if def_match:
                bad_variable = re.match("name '(.+)' is not defined", str(exception)).group(1)
                most_similar = levenshtein.most_similar(bad_variable, task.data.keys(), 3)
                error_msg = f'something you are referencing does not exist: ' \
                            f'"{exception}".'
                if len(most_similar) == 1:
                    error_msg += f' Did you mean \'{most_similar[0]}\'?'
                if len(most_similar) > 1:
                    error_msg += f' Did you mean one of \'{most_similar}\'?'

            else:
                error_msg = str(exception)
        super().__init__(task, error_msg, exception)


class WorkflowDataException(WorkflowException):

    def __init__(self, task, data_input=None, data_output=None, message=None):
        """
        :param task: the task that generated the error
        :param data_input: the spec of the input variable (if a data input)
        :param data_output: the spec of the output variable (if a data output)
        """
        super().__init__(task.task_spec, message or 'data object error')
        self.task = task
        self.data_input = data_input
        self.data_output = data_output
        self.task_trace = self.get_task_trace(task)
