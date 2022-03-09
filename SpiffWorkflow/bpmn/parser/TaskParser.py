# -*- coding: utf-8 -*-
from __future__ import division
from builtins import object
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

import logging
import sys
import traceback
from .ValidationException import ValidationException
from ..specs.BpmnProcessSpec import BpmnProcessSpec
from ..specs.ScriptTask import ScriptTask
from ..specs.UserTask import UserTask
from ..specs.events import _BoundaryEventParent, CancelEventDefinition
from ..specs.MultiInstanceTask import getDynamicMIClass
from ..specs.SubWorkflowTask import CallActivity, TransactionSubprocess
from ..specs.ExclusiveGateway import ExclusiveGateway
from ...dmn.specs.BusinessRuleTask import BusinessRuleTask
from ...operators import Attrib, PathAttrib
from .util import xpath_eval, one
from ...specs.SubWorkflow import SubWorkflow

LOG = logging.getLogger(__name__)

STANDARDLOOPCOUNT = '25'

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'


class TaskParser(object):
    """
    This class parses a single BPMN task node, and returns the Task Spec for
    that node.

    It also results in the recursive parsing of connected tasks, connecting all
    outgoing transitions, once the child tasks have all been parsed.
    """

    def __init__(self, process_parser, spec_class, node):
        """
        Constructor.

        :param process_parser: the owning process parser instance
        :param spec_class: the type of spec that should be created. This allows
          a subclass of BpmnParser to provide a specialised spec class, without
          extending the TaskParser.
        :param node: the XML node for this task
        """
        self.parser = process_parser.parser
        self.process_parser = process_parser
        self.spec_class = spec_class
        self.process_xpath = self.process_parser.xpath
        self.spec = self.process_parser.spec
        self.node = node
        self.xpath = xpath_eval(node)

    def _detect_multiinstance(self):

        # get special task decorators from XML
        multiinstanceElement = self.process_xpath(
            './/*[@id="%s"]/bpmn:multiInstanceLoopCharacteristics' % self.get_id())
        standardLoopElement = self.process_xpath(
            './/*[@id="%s"]/bpmn:standardLoopCharacteristics' % self.get_id())

        # initialize variables
        isMultiInstance = len(multiinstanceElement) > 0
        isLoop = len(standardLoopElement) > 0
        multiinstance = False
        isSequential = False
        completecondition = None
        collectionText = None
        elementVarText = None
        self.task.loopTask = False

        # Fix up MultiInstance mixin to take care of both
        # MultiInstance and standard Looping task
        if isMultiInstance or isLoop:
            multiinstance = True
            if isMultiInstance:
                sequentialText = multiinstanceElement[0].get('isSequential')
                collectionText = multiinstanceElement[0].attrib.get(
                    '{' + CAMUNDA_MODEL_NS + '}collection')
                elementVarText = multiinstanceElement[0].attrib.get(
                    '{' + CAMUNDA_MODEL_NS + '}elementVariable')

                if sequentialText == 'true':
                    isSequential = True
                loopCardinality = self.process_xpath(
                    './/*[@id="%s"]/bpmn:multiInstanceLoopCharacteristics/bpmn:loopCardinality' % self.get_id())
                if len(loopCardinality) > 0:
                    loopcount = loopCardinality[0].text
                elif collectionText is not None:
                    loopcount = collectionText
                else:
                    loopcount = '1'
                completionCondition = self.process_xpath(
                    './/*[@id="%s"]/bpmn:multiInstanceLoopCharacteristics/bpmn:completionCondition' % self.get_id())
                if len(completionCondition) > 0:
                    completecondition = completionCondition[0].text

            else: # must be loop
                isSequential = True
                loopcount = STANDARDLOOPCOUNT # here we default to a sane numer of loops
                self.task.loopTask = True
            LOG.debug("Task Name: %s - class %s" % (
            self.get_id(), self.task.__class__))
            LOG.debug("   Task is MultiInstance: %s" % multiinstance)
            LOG.debug("   MultiInstance is Sequential: %s" % isSequential)
            LOG.debug("   Task has loopcount of: %s" % loopcount)
            LOG.debug("   Class has name of : "
                      "%s" % self.task.__class__.__name__)
            # currently a safeguard that this isn't applied in any condition
            # that we do not expect. This list can be exapanded at a later
            # date To handle other use cases - don't forget the overridden
            # test classes!
        if multiinstance and isinstance(self.task, (UserTask,BusinessRuleTask,ScriptTask,CallActivity,SubWorkflow)):
            loopcount = loopcount.replace('.',
                                          '/')  # make dot notation compatible
            # with bmpmn path notation.

            if loopcount.find('/') >= 0:
                self.task.times = PathAttrib(loopcount)
            else:
                self.task.times = Attrib(loopcount)

            if collectionText is not None:
                collectionText = collectionText.replace('.', '/')  # make dot
                # notation compatible
                # with bmpmn path notation.
                if collectionText.find('/') >= 0:
                    self.task.collection = PathAttrib(collectionText)
                else:
                    self.task.collection = Attrib(collectionText)
            else:
                self.task.collection = None

            #  self.task.collection = collectionText
            self.task.elementVar = elementVarText
            self.task.completioncondition = completecondition  # we need to define what this is
            self.task.isSequential = isSequential
            # add some kind of limits here in terms of what kinds of classes
            # we will allow to be multiinstance

            self.task.prevtaskclass = self.task.__module__ + "." + self.task.__class__.__name__
            newtaskclass = getDynamicMIClass(self.get_id(),self.task.__class__)
            self.task.__class__ = newtaskclass
            # self.task.__class__ = type(self.get_id() + '_class', (
            #       MultiInstanceTask,self.task.__class__ ), {})
            self.task.multiInstance = multiinstance
            self.task.isSequential = isSequential

            if isLoop:
                self.task.expanded = 25
            else:
                self.task.expanded = 1

    def parse_node(self):
        """
        Parse this node, and all children, returning the connected task spec.
        """
        try:
            self.task = self.create_task()

            self.task.extensions = self.parser.parse_extensions(self.node,
                                                                xpath=self.xpath,
                                                                task_parser=self)
            self.task.documentation = self.parser._parse_documentation(
                self.node, xpath=self.xpath, task_parser=self)

            self._detect_multiinstance()

            boundary_event_nodes = self.process_xpath(
                './/bpmn:boundaryEvent[@attachedToRef="%s"]' % self.get_id())
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
                            filename=self.process_parser.filename)
                    parent_task.connect_outgoing(
                        b,
                        '%s.FromBoundaryEventParent' % boundary_event.get(
                            'id'),
                        None, None)
            else:
                self.process_parser.parsed_nodes[
                    self.node.get('id')] = self.task

            children = []
            outgoing = self.process_xpath(
                './/bpmn:sequenceFlow[@sourceRef="%s"]' % self.get_id())
            if len(outgoing) > 1 and not self.handles_multiple_outgoing():
                raise ValidationException(
                    'Multiple outgoing flows are not supported for '
                    'tasks of type',
                    node=self.node,
                    filename=self.process_parser.filename)
            for sequence_flow in outgoing:
                target_ref = sequence_flow.get('targetRef')
                try:
                    target_node = one(
                         self.process_xpath('.//bpmn:*[@id="%s"]'% \
                                target_ref))
                except:
                    raise ValidationException(
                        'When looking for a task spec, we found two items, '
                        'perhaps a form has the same ID? (%s)' % target_ref,
                        node=self.node,
                        filename=self.process_parser.filename)

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
            LOG.error("%r\n%s", ex, tb)
            raise ValidationException(
                "%r" % (ex), node=self.node,
                filename=self.process_parser.filename)

    def get_lane(self):
        """
        Return the name of the lane that contains this task
        """
        return self.process_parser.get_lane(self.get_id())

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
        Create an instance of the task appropriately. A subclass can override
        this method to get extra information from the node.
        """
        return self.spec_class(self.spec, self.get_task_spec_name(),
                               lane=self.get_lane(),
                               description=self.node.get('name', None),
                               position=self.process_parser.get_coord(self.get_id()))

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
            self.parser._parse_documentation(sequence_flow_node,
                                             task_parser=self))

    def handles_multiple_outgoing(self):
        """
        A subclass should override this method if the task supports multiple
        outgoing sequence flows.
        """
        return False
