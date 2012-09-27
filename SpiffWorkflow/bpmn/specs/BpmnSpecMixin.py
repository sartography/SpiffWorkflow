from SpiffWorkflow.Task import Task
from SpiffWorkflow.operators import Operator
from SpiffWorkflow.specs.TaskSpec import TaskSpec

__author__ = 'matth'

class _BpmnCondition(Operator):

    def __init__(self, *args):
        if len(args) > 1:
            raise TypeError("Too many arguments")
        super(_BpmnCondition, self).__init__(*args)

    def _matches(self, task):
        return task.workflow.script_engine.evaluate(task, self.args[0])

class SequenceFlow(object):
    """
    Keeps information relating to a sequence flow
    """

    def __init__(self, id, name, target_task_spec):
        """
        Constructor.
        """
        self.id = id
        self.name = name.strip() if name else name
        self.target_task_spec = target_task_spec

class BpmnSpecMixin(TaskSpec):
    """
    All BPMN spec classes should mix this superclass in. It adds a number of methods that are
    BPMN specific to the TaskSpec.
    """

    def __init__(self, parent, name, lane=None, **kwargs):
        """
        Constructor.

        :param lane: Indicates the name of the lane that this task belongs to (optional).
        """
        super(BpmnSpecMixin, self).__init__(parent, name, **kwargs)
        self.outgoing_sequence_flows = {}
        self.outgoing_sequence_flows_by_id = {}
        self.lane = lane

    def connect_outgoing(self, taskspec, sequence_flow_id, sequence_flow_name):
        """
        Connect this task spec to the indicated child.

        :param sequence_flow_id: The ID of the connecting sequenceFlow node.
        :param sequence_flow_name: The name of the connecting sequenceFlow node.
        """
        self.connect(taskspec)
        s = SequenceFlow(sequence_flow_id, sequence_flow_name, taskspec)
        self.outgoing_sequence_flows[taskspec.name] = s
        self.outgoing_sequence_flows_by_id[sequence_flow_id] = s

    def connect_outgoing_if(self, condition, taskspec, sequence_flow_id, sequence_flow_name):
        """
        Connect this task spec to the indicated child, if the condition evaluates to true.
        This should only be called if the task has a connect_if method (e.g. ExclusiveGateway).

        :param sequence_flow_id: The ID of the connecting sequenceFlow node.
        :param sequence_flow_name: The name of the connecting sequenceFlow node.
        """
        self.connect_if(_BpmnCondition(condition), taskspec)
        s = SequenceFlow(sequence_flow_id, sequence_flow_name, taskspec)
        self.outgoing_sequence_flows[taskspec.name] = s
        self.outgoing_sequence_flows_by_id[sequence_flow_id] = s

    def get_outgoing_sequence_flow_by_spec(self, task_spec):
        """
        Returns the outgoing SequenceFlow targeting the specified task_spec.
        """
        return self.outgoing_sequence_flows[task_spec.name]

    def get_outgoing_sequence_flow_by_id(self, id):
        """
        Returns the outgoing SequenceFlow with the specified ID.
        """
        return self.outgoing_sequence_flows_by_id[id]

    def has_outgoing_sequence_flow(self, id):
        """
        Returns true if the SequenceFlow with the specified ID is leaving this task.
        """
        return id in self.outgoing_sequence_flows_by_id

    def get_outgoing_sequence_names(self):
        """
        Returns a list of the names of outgoing sequences. Some may be None.
        """
        return sorted([s.name for s in self.outgoing_sequence_flows_by_id.itervalues()])

    def accept_message(self, my_task, message):
        """
        A subclass should override this method if they want to be notified of the receipt of a message
        when in a WAITING state.

        Returns True if the task did process the message.
        """
        return False

    ######### Hooks for Custom BPMN tasks ##########

    def entering_waiting_state(self, my_task):
        """
        Called when a task enters the WAITING state.

        A subclass may override this method to do work when this happens.
        """
        pass

    def entering_ready_state(self, my_task):
        """
        Called when a task enters the READY state.

        A subclass may override this method to do work when this happens.
        """
        pass

    def entering_complete_state(self, my_task):
        """
        Called when a task enters the COMPLETE state.

        A subclass may override this method to do work when this happens.
        """
        pass

    def entering_cancelled_state(self, my_task):
        """
        Called when a task enters the CANCELLED state.

        A subclass may override this method to do work when this happens.
        """
        pass

    ################################################

    def _on_complete_hook(self, my_task):
        super(BpmnSpecMixin, self)._on_complete_hook(my_task)
        if isinstance(my_task.parent.task_spec, BpmnSpecMixin):
            my_task.parent.task_spec._child_complete_hook(my_task)
        if not my_task.workflow._is_busy_with_restore():
            self.entering_complete_state(my_task)

    def _child_complete_hook(self, child_task):
        pass

    def _on_cancel(self, my_task):
        super(BpmnSpecMixin, self)._on_cancel(my_task)
        my_task.workflow._task_cancelled_notify(my_task)
        if not my_task.workflow._is_busy_with_restore():
            self.entering_cancelled_state(my_task)

    def _update_state_hook(self, my_task):
        prev_state = my_task.state
        super(BpmnSpecMixin, self)._update_state_hook(my_task)
        if prev_state != Task.WAITING and my_task.state == Task.WAITING and not my_task.workflow._is_busy_with_restore():
            self.entering_waiting_state(my_task)

    def _on_ready_before_hook(self, my_task):
        super(BpmnSpecMixin, self)._on_ready_before_hook(my_task)
        if not my_task.workflow._is_busy_with_restore():
            self.entering_ready_state(my_task)


