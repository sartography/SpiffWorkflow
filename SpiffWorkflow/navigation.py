import copy

from . import WorkflowException
from .bpmn.specs.events import StartEvent, EndEvent, IntermediateCatchEvent, IntermediateThrowEvent, BoundaryEvent, _BoundaryEventParent
from .bpmn.specs.ExclusiveGateway import ExclusiveGateway
from .bpmn.specs.ManualTask import ManualTask
from .bpmn.specs.NoneTask import NoneTask
from .bpmn.specs.ParallelGateway import ParallelGateway
from .bpmn.specs.ScriptTask import ScriptTask
from .bpmn.specs.UserTask import UserTask
from .dmn.specs.BusinessRuleTask import BusinessRuleTask
from .specs import CancelTask, StartTask
from .task import TaskStateNames, TaskState
from .bpmn.specs.BpmnSpecMixin import BpmnSpecMixin, SequenceFlow
from .bpmn.specs.UnstructuredJoin import UnstructuredJoin
from .bpmn.specs.MultiInstanceTask import MultiInstanceTask
from .bpmn.specs.SubWorkflowTask import SubWorkflowTask, CallActivity, TransactionSubprocess


class NavItem(object):
    """
        A waypoint in a workflow along with some key metrics
        - Each list item has :
           spec_id          -   TaskSpec or Sequence flow id
           name             -   The name of the task spec (or sequence)
           spec_type        -   The type of task spec (it's class name)
           task_id          -   The uuid of the actual task instance, if it exists
           description      -   Text description
           backtrack_to     -   The spec_id of the task this will back track to.
           indent           -   A hint for indentation
           lane             -   This is the lane for the task if indicated.
           state            -   State of the task
    """

    def __init__(self, spec_id, name, description,
                 lane=None, backtrack_to=None, indent=0):
        self.spec_id = spec_id
        self.name = name
        self.spec_type = "None"
        self.description = description
        self.lane = lane
        self.backtrack_to = backtrack_to
        self.indent = indent
        self.task_id = None
        self.state = None
        self.children = []

    def additional_spec_types(self):
        """ALlow subclasses to provide additional spec types."""
        pass

    def name_for_unknown_spec(self, spec):
        """Allow subclasses to provide a name for an unknown spec."""
        pass

    def set_spec_type(self, spec):
        additional_spec_types = self.additional_spec_types() or []
        types = [CancelTask, StartTask] + additional_spec_types

        for t in types:
            if isinstance(spec, t):
                self.spec_type = t.__name__
                return

        self.spec_type = self.name_for_unknown_spec(spec)
        if self.spec_type is None:
            raise WorkflowException(spec, "Unknown spec: " + spec.__class__.__name__)

    @classmethod
    def from_spec(cls, spec: BpmnSpecMixin, backtrack_to=None, indent=None):
        instance = cls(
            spec_id=spec.id,
            name=spec.name,
            description=spec.description,
            lane=spec.lane,
            backtrack_to=backtrack_to,
            indent=indent
        )
        instance.set_spec_type(spec)
        return instance

    @classmethod
    def from_flow(cls, flow: SequenceFlow, lane, backtrack_to, indent):
        """We include flows in the navigation if we hit a conditional gateway,
        as in do this if x, do this if y...."""
        instance = cls(
            spec_id=flow.id,
            name=flow.name,
            description=flow.name,
            lane=lane,
            backtrack_to=backtrack_to,
            indent=indent
        )
        instance.set_spec_type(flow)
        return instance

    def __eq__(self, other):
        if isinstance(other, NavItem):
            return self.spec_id == other.spec_id and \
                   self.name == other.name and \
                   self.spec_type == other.spec_type and \
                   self.description == other.description and \
                   self.lane == other.lane and \
                   self.backtrack_to == other.backtrack_to and \
                   self.indent == other.indent
        return False

    def __str__(self):
        text = self.description
        if self.spec_type == "StartEvent":
            text = "O"
        elif self.spec_type == "TaskEndEvent":
            text = "@"
        elif self.spec_type == "ExclusiveGateway":
            text = f"X {text} X"
        elif self.spec_type == "ParallelGateway":
            text = f"+ {text}"
        elif self.spec_type == "SequenceFlow":
            text = f"-> {text}"
        elif self.spec_type[-4:] == "Task":
            text = f"[{text}] TASK ID: {self.task_id}"
        else:
            text = f"({self.spec_type}) {text}"

        result = f' {"..," * self.indent} STATE: {self.state} {text}'
        if self.lane:
            result = f'|{self.lane}| {result}'
        if self.backtrack_to:
            result += f"  (BACKTRACK to {self.backtrack_to}"

        return result
