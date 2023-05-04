
from SpiffWorkflow.bpmn.exceptions import WorkflowDataException
from SpiffWorkflow.operators import Operator
from SpiffWorkflow.specs.base import TaskSpec


class _BpmnCondition(Operator):

    def __init__(self, *args):
        if len(args) > 1:
            raise TypeError("Too many arguments")
        super(_BpmnCondition, self).__init__(*args)

    def _matches(self, task):
        return task.workflow.script_engine.evaluate(task, self.args[0])


class BpmnTaskSpec(TaskSpec):
    """This class provides BPMN-specific attributes."""

    def __init__(self, wf_spec, name, lane=None, documentation=None, 
                 data_input_associations=None, data_output_associations=None, **kwargs):
        """
        Constructor.

        :param lane: Indicates the name of the lane that this task belongs to
        (optional).
        """
        super().__init__(wf_spec, name, **kwargs)
        self.lane = lane
        self.documentation = documentation
        self.data_input_associations = data_input_associations or []
        self.data_output_associations = data_output_associations or []
        self.io_specification = None

    @property
    def spec_type(self):
        return 'BPMN Task'

    def connect_outgoing_if(self, condition, taskspec):
        """
        Connect this task spec to the indicated child, if the condition
        evaluates to true. This should only be called if the task has a
        connect_if method (e.g. ExclusiveGateway).
        """
        if condition is None:
            self.connect(taskspec)
        else:
            self.connect_if(_BpmnCondition(condition), taskspec)

    def _update_hook(self, my_task):

        super()._update_hook(my_task)
        # This copies data from data objects
        for obj in self.data_input_associations:
            obj.get(my_task)

        # If an IO spec was given, require all inputs are present, and remove all other inputs.
        if self.io_specification is not None and len(self.io_specification.data_inputs) > 0:
            data = {}
            for var in self.io_specification.data_inputs:
                if var.name not in my_task.data:
                    raise WorkflowDataException(f"Missing data input", task=my_task, data_input=var)
                data[var.name] = my_task.data[var.name]
            my_task.data = data

        return True

    def _on_complete_hook(self, my_task):

        my_task.parent.task_spec._child_complete_hook(my_task)

        if self.io_specification is not None and len(self.io_specification.data_outputs) > 0:
            data = {}
            for var in self.io_specification.data_outputs:
                if var.name not in my_task.data:
                    raise WorkflowDataException(f"Missing data ouput", task=my_task, data_output=var)
                data[var.name] = my_task.data[var.name]
            my_task.data = data

        for obj in self.data_output_associations:
            obj.set(my_task)

        for obj in self.data_input_associations:
            # Remove the any copied input variables that might not have already been removed
            my_task.data.pop(obj.name, None)

        super()._on_complete_hook(my_task)

    def _child_complete_hook(self, child_task):
        pass
