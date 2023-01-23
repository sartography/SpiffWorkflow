from SpiffWorkflow.exceptions import WorkflowException


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
