from SpiffWorkflow.exceptions import WorkflowTaskException


class WorkflowDataException(WorkflowTaskException):

    def __init__(self, message, task, data_input=None, data_output=None):
        """
        :param task: the task that generated the error
        :param data_input: the spec of the input variable (if a data input)
        :param data_output: the spec of the output variable (if a data output)
        """
        super().__init__(message, task)
        self.data_input = data_input
        self.data_output = data_output
