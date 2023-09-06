
from SpiffWorkflow.bpmn.exceptions import WorkflowDataException
from SpiffWorkflow.operators import Operator
from SpiffWorkflow.specs.base import TaskSpec


class _BpmnCondition(Operator):

    def __init__(self, *args):
        if len(args) > 1:
            raise TypeError("Too many arguments")
        super(_BpmnCondition, self).__init__(*args)

    def _matches(self, task):
        return task.workflow.script_engine.evaluate(task, self.args[0], external_methods=task.workflow.data)


class BpmnTaskSpec(TaskSpec):
    """
    This class provides BPMN-specific attributes.

    It is intended to be used with all tasks in a BPMN workflow.  Spiff internal tasks (such
    as Root, EndJoin, etc) inherit directly from this.

    Visible tasks inherit from `BpmnSpecMixin`, which will assign the `bpmn_id` and `bpmn_name`.

    The intent is to (1) give all tasks in the workflow the same attributes and (2) provide an
    easy way of knowing whether a task appearson the diagram.
    """
    def __init__(self, wf_spec, name, lane=None, documentation=None,
                 data_input_associations=None, data_output_associations=None, **kwargs):
        """
        :param lane: Indicates the name of the lane that this task belongs to
        :param documentation: the contents of the documentation element
        :param data_input_associations: a list of data references to be used as inputs to the task
        :param data_output_associations: a list of data references to be used as inputs to the task
        """
        super().__init__(wf_spec, name, **kwargs)
        self.bpmn_id = None
        self.bpmn_name = None
        self.lane = lane
        self.documentation = documentation
        self.data_input_associations = data_input_associations or []
        self.data_output_associations = data_output_associations or []
        self.io_specification = None
        if self.description is None:
            self.description = 'BPMN Task'

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
                if var.bpmn_id not in my_task.data:
                    raise WorkflowDataException("Missing data input", task=my_task, data_input=var)
                data[var.bpmn_id] = my_task.data[var.bpmn_id]
            my_task.data = data

        return True

    def _on_complete_hook(self, my_task):

        if self.io_specification is not None and len(self.io_specification.data_outputs) > 0:
            data = {}
            for var in self.io_specification.data_outputs:
                if var.bpmn_id not in my_task.data:
                    raise WorkflowDataException("Missing data ouput", task=my_task, data_output=var)
                data[var.bpmn_id] = my_task.data[var.bpmn_id]
            my_task.data = data

        for obj in self.data_output_associations:
            obj.set(my_task)

        for obj in self.data_input_associations:
            # Remove the any copied input variables that might not have already been removed
            my_task.data.pop(obj.bpmn_id, None)

        super()._on_complete_hook(my_task)

    def task_info(self, my_task):
        # This method can be extended to provide task specific info for different spec types
        # Since almost all spec types can be MI, add instance info here if present
        info = {}
        if 'key_or_index' in my_task.internal_data:
            info['instance'] = my_task.internal_data.get('key_or_index')
        if 'item' in my_task.internal_data:
            info['instance'] = my_task.internal_data.get('item')
        if 'iteration' in my_task.internal_data:
            info['iteration'] = my_task.internal_data.get('iteration')
        return info
