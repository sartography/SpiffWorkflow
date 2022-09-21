import copy

from ..navigation import NavItem as CoreNavItem
from ..exceptions import WorkflowException
from .specs.events import StartEvent, EndEvent, IntermediateCatchEvent, IntermediateThrowEvent, BoundaryEvent, _BoundaryEventParent
from .specs.ExclusiveGateway import ExclusiveGateway
from .specs.ManualTask import ManualTask
from .specs.NoneTask import NoneTask
from .specs.ParallelGateway import ParallelGateway
from .specs.ScriptTask import ScriptTask
from .specs.UserTask import UserTask
from ..dmn.specs.BusinessRuleTask import BusinessRuleTask
from ..task import TaskStateNames, TaskState
from .specs.BpmnSpecMixin import BpmnSpecMixin, SequenceFlow
from .specs.UnstructuredJoin import UnstructuredJoin
from .specs.MultiInstanceTask import MultiInstanceTask
from .specs.SubWorkflowTask import SubWorkflowTask, CallActivity, TransactionSubprocess


class NavItem(CoreNavItem):

    def additional_spec_types(self):
        return [UserTask, ManualTask, BusinessRuleTask, ScriptTask, EndEvent,
                StartEvent, MultiInstanceTask, SequenceFlow, ExclusiveGateway,
                ParallelGateway, CallActivity, TransactionSubprocess,
                UnstructuredJoin, NoneTask, BoundaryEvent,
                IntermediateThrowEvent, IntermediateCatchEvent]

    def name_for_unknown_spec(self, spec):
        class_name = spec.__class__.__name__

        # These should be removed at some point in the process.
        return class_name if class_name.startswith('_') else None

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
