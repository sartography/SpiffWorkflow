from SpiffWorkflow.bpmn.specs.BoundaryEvent import BoundaryEventParent
from SpiffWorkflow.bpmn.parser.util import *

__author__ = 'matth'

class TaskParser(object):
    """
    This class parses a single BPMN task node, and returns the Task Spec for that node.

    It also results in the recursive parsing of connected tasks, connecting all
    outgoing transitions, once the child tasks have all been parsed.
    """

    def __init__(self, process_parser, spec_class, node):
        """
        Constructor.

        :param process_parser: the owning process parser instance
        :param spec_class: the type of spec that should be created. This allows a subclass of BpmnParser to
        provide a specialised spec class, without extending the TaskParser.
        :param node: the XML node for this task
        """
        self.parser = process_parser.parser
        self.process_parser = process_parser
        self.spec_class = spec_class
        self.process_xpath = self.process_parser.xpath
        self.spec = self.process_parser.spec
        self.node = node
        self.xpath = xpath_eval(node)

    def parse_node(self):
        """
        Parse this node, and all children, returning the connected task spec.
        """

        self.task = self.create_task()

        boundary_event_nodes = self.process_xpath('.//bpmn:boundaryEvent[@attachedToRef="%s"]' % self.get_id())
        if boundary_event_nodes:
            parent_task = BoundaryEventParent(self.spec, '%s.BoundaryEventParent' % self.get_id(), self.task, lane=self.task.lane)
            self.process_parser.parsed_nodes[self.node.get('id')] = parent_task

            parent_task.connect_outgoing(self.task, '%s.FromBoundaryEventParent' % self.get_id(), None)
            for boundary_event in boundary_event_nodes:
                b = self.process_parser.parse_node(boundary_event)
                parent_task.connect_outgoing(b, '%s.FromBoundaryEventParent' % boundary_event.get('id'), None)
        else:
            self.process_parser.parsed_nodes[self.node.get('id')] = self.task


        children = []
        outgoing = self.process_xpath('.//bpmn:sequenceFlow[@sourceRef="%s"]' % self.get_id())
        if len(outgoing) > 1 and not self.handles_multiple_outgoing():
            raise NotImplementedError('Multiple outgoing flows are not supported for tasks of type %s', self.spec_class.__name__)
        for sequence_flow in outgoing:
            target_ref = sequence_flow.get('targetRef')
            target_node = one(self.process_xpath('.//bpmn:*[@id="%s"]' % target_ref))
            c = self.process_parser.parse_node(target_node)
            children.append((c, target_node, sequence_flow))

        if children:
            default_outgoing = self.node.get('default')
            if not default_outgoing:
                (c, target_node, sequence_flow) = children[0]
                default_outgoing = sequence_flow.get('id')

            for (c, target_node, sequence_flow) in children:
                self.connect_outgoing(c, target_node, sequence_flow, sequence_flow.get('id') == default_outgoing)

        return parent_task if boundary_event_nodes else self.task

    def get_lane(self):
        """
        Return the name of the lane that contains this task
        """
        lane_match = self.process_xpath('.//bpmn:lane/bpmn:flowNodeRef[text()="%s"]/..' % self.get_id())
        assert len(lane_match)<= 1
        return lane_match[0].get('name') if lane_match else None


    def get_task_spec_name(self, target_ref=None):
        """
        Returns a unique task spec name for this task (or the targeted one)
        """
        return target_ref or self.get_id()

    def get_id(self):
        """
        Return the node ID
        """
        return self.node.get('id')

    def create_task(self):
        """
        Create an instance of the task appropriately. A subclass can override this method to get extra information from the node.
        """
        return self.spec_class(self.spec, self.get_task_spec_name(), lane=self.get_lane(), description=self.node.get('name', None))

    def connect_outgoing(self, outgoing_task, outgoing_task_node, sequence_flow_node, is_default):
        """
        Connects this task to the indicating outgoing task, with the details in the sequence flow.
        A subclass can override this method to get extra information from the node.
        """
        self.task.connect_outgoing(outgoing_task, sequence_flow_node.get('id'), sequence_flow_node.get('name', None))

    def handles_multiple_outgoing(self):
        """
        A subclass should override this method if the task supports multiple outgoing sequence flows.
        """
        return False

    def is_parallel_branching(self):
        """
        A subclass should override this method to indicate whether this task represents a parallel branch point.

        By default this returns true is more than one outgoing sequence flows.
        """
        return len(self.task.outputs) > 1
