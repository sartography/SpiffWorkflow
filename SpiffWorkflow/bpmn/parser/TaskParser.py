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

from .ValidationException import ValidationException
from ..specs.events.IntermediateEvent import _BoundaryEventParent
from ..specs.events.event_definitions import CancelEventDefinition
from ..specs.MultiInstanceTask import StandardLoopTask, SequentialMultiInstanceTask, ParallelMultiInstanceTask
from ..specs.SubWorkflowTask import TransactionSubprocess
from ..specs.ExclusiveGateway import ExclusiveGateway
from ..specs.InclusiveGateway import InclusiveGateway
from ..specs.data_spec import TaskDataReference

from .util import one
from .node_parser import NodeParser

CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'


class TaskParser(NodeParser):
    """
    This class parses a single BPMN task node, and returns the Task Spec for
    that node.

    It also results in the recursive parsing of connected tasks, connecting all
    outgoing transitions, once the child tasks have all been parsed.
    """

    def __init__(self, process_parser, spec_class, node, nsmap=None, lane=None):
        """
        Constructor.

        :param process_parser: the owning process parser instance
        :param spec_class: the type of spec that should be created. This allows
          a subclass of BpmnParser to provide a specialised spec class, without
          extending the TaskParser.
        :param node: the XML node for this task
        """
        super().__init__(node, nsmap, filename=process_parser.filename, lane=lane)
        self.process_parser = process_parser
        self.spec_class = spec_class
        self.spec = self.process_parser.spec

    def _copy_task_attrs(self, original):

        self.task.inputs = original.inputs
        self.task.outputs = original.outputs
        self.task.io_specification = original.io_specification
        self.task.data_input_associations = original.data_input_associations
        self.task.data_output_associations = original.data_output_associations
        self.task.description = original.description

        original.inputs = [self.task]
        original.outputs = []
        original.io_specification = None
        original.data_input_associations = []
        original.data_output_associations = []
        original.name = f'{original.name} [child]'
        self.task.task_spec = original.name
        self.spec.task_specs[original.name] = original

    def _add_loop_task(self, loop_characteristics):

        maximum = loop_characteristics.attrib.get('loopMaximum')
        if maximum is not None:
            maximum = int(maximum)
        condition = self.xpath('./bpmn:standardLoopCharacteristics/bpmn:loopCondition')
        condition = condition[0].text if len(condition) > 0 else None
        test_before = loop_characteristics.get('testBefore', 'false') == 'true'
        if maximum is None and condition is None:
            self.raise_validation_exception('A loopMaximum or loopCondition must be specified for Loop Tasks')

        original = self.spec.task_specs.pop(self.task.name)
        self.task = StandardLoopTask(self.spec, original.name, '', maximum, condition, test_before)
        self._copy_task_attrs(original)

    def _add_multiinstance_task(self, loop_characteristics):
        
        sequential = loop_characteristics.get('isSequential') == 'true'
        prefix = 'bpmn:multiInstanceLoopCharacteristics'
        cardinality = self.xpath(f'./{prefix}/bpmn:loopCardinality')
        loop_input = self.xpath(f'./{prefix}/bpmn:loopDataInputRef')
        if len(cardinality) == 0 and len(loop_input) == 0:
            self.raise_validation_exception("A multiinstance task must specify a cardinality or a loop input data reference")
        elif len(cardinality) > 0 and len(loop_input) > 0:
            self.raise_validation_exception("A multiinstance task must specify exactly one of cardinality or loop input data reference")
        cardinality = int(cardinality[0].text) if len(cardinality) > 0 else None

        loop_input = loop_input[0].text if len(loop_input) > 0 else None
        if loop_input is not None and self.task.io_specification is not None:
            try:
                loop_input = [v for v in self.task.io_specification.data_inputs if v.name == loop_input][0]
            except:
                self.raise_validation_exception('The loop input data reference is missing from the IO specification')

        input_item = self.xpath(f'./{prefix}/bpmn:inputDataItem')
        input_item = self.create_data_spec(input_item[0], TaskDataReference) if len(input_item) > 0 else None

        loop_output = self.xpath(f'./{prefix}/bpmn:loopDataOutputRef')
        loop_output = loop_output[0].text if len(loop_output) > 0 else None
        if loop_output is not None and self.task.io_specification is not None:
            try:
                refs = set(self.task.io_specification.data_inputs + self.task.io_specification.data_outputs)
                loop_output = [v for v in refs if v.name == loop_output][0]
            except:
                self.raise_validation_exception('The loop output data reference is missing from the IO specification')

        output_item = self.xpath(f'./{prefix}/bpmn:outputDataItem')
        output_item = self.create_data_spec(output_item[0], TaskDataReference) if len(output_item) > 0 else None

        condition = self.xpath(f'./{prefix}/bpmn:completionCondition')
        condition = condition[0].text if len(condition) > 0 else None

        original = self.spec.task_specs.pop(self.task.name)
        params = {
            'task_spec': '', 
            'cardinality': cardinality, 
            'data_input': loop_input,
            'data_output':loop_output,
            'input_item': input_item,
            'output_item': output_item,
            'condition': condition,
        }
        if sequential:
            self.task = SequentialMultiInstanceTask(self.spec, original.name, **params)
        else:
            self.task = ParallelMultiInstanceTask(self.spec, original.name, **params)
        self._copy_task_attrs(original)

    def _add_boundary_event(self, children):

        parent = _BoundaryEventParent(
            self.spec, '%s.BoundaryEventParent' % self.get_id(),
            self.task, lane=self.task.lane)
        self.process_parser.parsed_nodes[self.node.get('id')] = parent
        parent.connect(self.task)
        for event in children:
            child = self.process_parser.parse_node(event)
            if isinstance(child.event_definition, CancelEventDefinition) \
              and not isinstance(self.task, TransactionSubprocess):
                self.raise_validation_exception('Cancel Events may only be used with transactions')
            parent.connect(child)
        return parent

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

            io_spec = self.xpath('./bpmn:ioSpecification')
            if len(io_spec) > 0:
                self.task.io_specification = self.parse_io_spec()

            loop_characteristics = self.xpath('./bpmn:standardLoopCharacteristics')
            if len(loop_characteristics) > 0:
                self._add_loop_task(loop_characteristics[0])

            mi_loop_characteristics = self.xpath('./bpmn:multiInstanceLoopCharacteristics')
            if len(mi_loop_characteristics) > 0:
                self._add_multiinstance_task(mi_loop_characteristics[0])

            boundary_event_nodes = self.doc_xpath('.//bpmn:boundaryEvent[@attachedToRef="%s"]' % self.get_id())
            if boundary_event_nodes:
                parent = self._add_boundary_event(boundary_event_nodes)
            else:
                self.process_parser.parsed_nodes[self.node.get('id')] = self.task

            children = []
            outgoing = self.doc_xpath('.//bpmn:sequenceFlow[@sourceRef="%s"]' % self.get_id())
            if len(outgoing) > 1 and not self.handles_multiple_outgoing():
                self.raise_validation_exception('Multiple outgoing flows are not supported for tasks of type')
            for sequence_flow in outgoing:
                target_ref = sequence_flow.get('targetRef')
                try:
                    target_node = one(self.doc_xpath('.//bpmn:*[@id="%s"]'% target_ref))
                except:
                    self.raise_validation_exception('When looking for a task spec, we found two items, '
                        'perhaps a form has the same ID? (%s)' % target_ref)

                c = self.process_parser.parse_node(target_node)
                position = c.position
                children.append((position, c, target_node, sequence_flow))

            if children:
                # Sort children by their y coordinate.
                children = sorted(children, key=lambda tup: float(tup[0]["y"]))

                default_outgoing = self.node.get('default')
                if len(children) == 1 and isinstance(self.task, (ExclusiveGateway, InclusiveGateway)):
                    (position, c, target_node, sequence_flow) = children[0]
                    if self.parse_condition(sequence_flow) is None:
                        default_outgoing = sequence_flow.get('id')

                for (position, c, target_node, sequence_flow) in children:
                    self.connect_outgoing(c, sequence_flow, sequence_flow.get('id') == default_outgoing)

            return parent if boundary_event_nodes else self.task
        except ValidationException as ve:
            raise ve
        except Exception as ex:
            raise ValidationException("%r" % (ex), node=self.node, file_name=self.filename)

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

    def connect_outgoing(self, outgoing_task, sequence_flow_node, is_default):
        """
        Connects this task to the indicating outgoing task, with the details in
        the sequence flow. A subclass can override this method to get extra
        information from the node.
        """
        self.task.connect(outgoing_task)

    def handles_multiple_outgoing(self):
        """
        A subclass should override this method if the task supports multiple
        outgoing sequence flows.
        """
        return False

