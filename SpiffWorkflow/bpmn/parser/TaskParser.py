# -*- coding: utf-8 -*-

# Copyright (C) 2012 Matthew Hampton
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

import sys
import traceback
from .ValidationException import ValidationException
from ..specs.NoneTask import NoneTask
from ..specs.ScriptTask import ScriptTask
from ..specs.UserTask import UserTask
from ..specs.events import _BoundaryEventParent, CancelEventDefinition
from ..specs.MultiInstanceTask import getDynamicMIClass
from ..specs.SubWorkflowTask import CallActivity, TransactionSubprocess, SubWorkflowTask
from ..specs.ExclusiveGateway import ExclusiveGateway
from ...dmn.specs.BusinessRuleTask import BusinessRuleTask
from ...operators import Attrib, PathAttrib
from .util import one, first
from .node_parser import NodeParser

STANDARDLOOPCOUNT = '25'

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'


class TaskParser(NodeParser):
    """
    This class parses a single BPMN task node, and returns the Task Spec for
    that node.

    It also results in the recursive parsing of connected tasks, connecting all
    outgoing transitions, once the child tasks have all been parsed.
    """

    def __init__(self, process_parser, spec_class, node, lane=None):
        """
        Constructor.

        :param process_parser: the owning process parser instance
        :param spec_class: the type of spec that should be created. This allows
          a subclass of BpmnParser to provide a specialised spec class, without
          extending the TaskParser.
        :param node: the XML node for this task
        """
        super().__init__(node, process_parser.filename, process_parser.doc_xpath, lane)
        self.process_parser = process_parser
        self.spec_class = spec_class
        self.spec = self.process_parser.spec

    def _set_multiinstance_attributes(self, is_sequential, expanded, loop_count,
                                      loop_task=False, element_var=None, collection=None, completion_condition=None):
        # This should be replaced with its own task parser (though I'm not sure how feasible this is given
        # the current parser achitecture).  We should also consider separate classes for loop vs
        # multiinstance because having all these optional attributes is a nightmare

        if not isinstance(self.task, (NoneTask, UserTask, BusinessRuleTask, ScriptTask, CallActivity, SubWorkflowTask)):
            raise ValidationException(
                f'Unsupported MultiInstance Task: {self.task.__class__}',
                node=self.node,
                filename=self.filename)

        self.task.loopTask = loop_task
        self.task.isSequential = is_sequential
        self.task.expanded = expanded
        # make dot notation compatible with bmpmn path notation.
        self.task.times = PathAttrib(loop_count.replace('.', '/')) if loop_count.find('.') > 0 else Attrib(loop_count)
        self.task.elementVar = element_var
        self.task.collection = collection
        self.task.completioncondition = completion_condition

        self.task.prevtaskclass = self.task.__module__ + "." + self.task.__class__.__name__
        newtaskclass = getDynamicMIClass(self.get_id(),self.task.__class__)
        self.task.__class__ = newtaskclass

    def _detect_multiinstance(self):

        multiinstance_element = first(self.xpath('./bpmn:multiInstanceLoopCharacteristics'))
        if multiinstance_element is not None:
            is_sequential = multiinstance_element.get('isSequential') == 'true'

            element_var_text = multiinstance_element.attrib.get('{' + CAMUNDA_MODEL_NS + '}elementVariable')
            collection_text = multiinstance_element.attrib.get('{' + CAMUNDA_MODEL_NS + '}collection')

            loop_cardinality = first(self.xpath('./bpmn:multiInstanceLoopCharacteristics/bpmn:loopCardinality'))
            if loop_cardinality is not None:
                loop_count = loop_cardinality.text
            elif collection_text is not None:
                loop_count = collection_text
            else:
                loop_count = '1'

            if collection_text is not None:
                collection = PathAttrib(collection_text.replace('.', '/')) if collection_text.find('.') > 0 else Attrib(collection_text)
            else:
                collection = None

            completion_condition = first(self.xpath('./bpmn:multiInstanceLoopCharacteristics/bpmn:completionCondition'))
            if completion_condition is not None:
                completion_condition = completion_condition.text

            self._set_multiinstance_attributes(is_sequential, 1, loop_count,
                                               element_var=element_var_text,
                                               collection=collection,
                                               completion_condition=completion_condition)

        elif len(self.xpath('./bpmn:standardLoopCharacteristics')) > 0:
            self._set_multiinstance_attributes(True, 25, STANDARDLOOPCOUNT, loop_task=True)

    def parse_node(self):
        """
        Parse this node, and all children, returning the connected task spec.
        """
        try:
            self.task = self.create_task()
            # Why do we just set random attributes willy nilly everywhere in the code????
            # And we still pass around a gigantic kwargs dict whenever we create anything!
            self.task.extensions = self.parse_extensions()
            self.task.documentation = self.parse_documentation()
            # And now I have to add more of the same crappy thing.
            self.task.data_input_associations = self.parse_incoming_data_references()
            self.task.data_output_associations = self.parse_outgoing_data_references()

            self._detect_multiinstance()

            boundary_event_nodes = self.doc_xpath('.//bpmn:boundaryEvent[@attachedToRef="%s"]' % self.get_id())
            if boundary_event_nodes:
                parent_task = _BoundaryEventParent(
                    self.spec, '%s.BoundaryEventParent' % self.get_id(),
                    self.task, lane=self.task.lane)
                self.process_parser.parsed_nodes[
                    self.node.get('id')] = parent_task
                parent_task.connect_outgoing(
                    self.task, '%s.FromBoundaryEventParent' % self.get_id(),
                    None, None)
                for boundary_event in boundary_event_nodes:
                    b = self.process_parser.parse_node(boundary_event)
                    if isinstance(b.event_definition, CancelEventDefinition) \
                      and not isinstance(self.task, TransactionSubprocess):
                        raise ValidationException(
                            'Cancel Events may only be used with transactions',
                            node=self.node,
                            filename=self.filename)
                    parent_task.connect_outgoing(
                        b,
                        '%s.FromBoundaryEventParent' % boundary_event.get(
                            'id'),
                        None, None)
            else:
                self.process_parser.parsed_nodes[
                    self.node.get('id')] = self.task

            children = []
            outgoing = self.doc_xpath('.//bpmn:sequenceFlow[@sourceRef="%s"]' % self.get_id())
            if len(outgoing) > 1 and not self.handles_multiple_outgoing():
                raise ValidationException(
                    'Multiple outgoing flows are not supported for '
                    'tasks of type',
                    node=self.node,
                    filename=self.filename)
            for sequence_flow in outgoing:
                target_ref = sequence_flow.get('targetRef')
                try:
                    target_node = one(self.doc_xpath('.//bpmn:*[@id="%s"]'% target_ref))
                except:
                    raise ValidationException(
                        'When looking for a task spec, we found two items, '
                        'perhaps a form has the same ID? (%s)' % target_ref,
                        node=self.node,
                        filename=self.filename)

                c = self.process_parser.parse_node(target_node)
                position = c.position
                children.append((position, c, target_node, sequence_flow))

            if children:
                # Sort children by their y coordinate.
                children = sorted(children, key=lambda tup: float(tup[0]["y"]))

                default_outgoing = self.node.get('default')
                if not default_outgoing:
                    if len(children) == 1 or not isinstance(self.task, ExclusiveGateway):
                        (position, c, target_node, sequence_flow) = children[0]
                        default_outgoing = sequence_flow.get('id')

                for (position, c, target_node, sequence_flow) in children:
                    self.connect_outgoing(
                        c, target_node, sequence_flow,
                        sequence_flow.get('id') == default_outgoing)

            return parent_task if boundary_event_nodes else self.task
        except ValidationException:
            raise
        except Exception as ex:
            exc_info = sys.exc_info()
            tb = "".join(traceback.format_exception(
                exc_info[0], exc_info[1], exc_info[2]))
            raise ValidationException("%r" % (ex), node=self.node, filename=self.filename)

    def get_task_spec_name(self, target_ref=None):
        """
        Returns a unique task spec name for this task (or the targeted one)
        """
        return target_ref or self.get_id()

    def create_task(self):
        """
        Create an instance of the task appropriately. A subclass can override
        this method to get extra information from the node.
        """
        return self.spec_class(self.spec, self.get_task_spec_name(),
                               lane=self.lane,
                               description=self.node.get('name', None),
                               position=self.position)

    def connect_outgoing(self, outgoing_task, outgoing_task_node,
                         sequence_flow_node, is_default):
        """
        Connects this task to the indicating outgoing task, with the details in
        the sequence flow. A subclass can override this method to get extra
        information from the node.
        """
        self.task.connect_outgoing(
            outgoing_task, sequence_flow_node.get('id'),
            sequence_flow_node.get(
                'name', None),
            self.parse_documentation(sequence_flow_node))

    def handles_multiple_outgoing(self):
        """
        A subclass should override this method if the task supports multiple
        outgoing sequence flows.
        """
        return False
