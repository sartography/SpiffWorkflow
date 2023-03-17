# -*- coding: utf-8 -*-

# Copyright (C) 2007-2012 Samuel Abels
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
from .. import operators
from ..specs.Simple import Simple
from ..specs.WorkflowSpec import WorkflowSpec
from ..exceptions import SpiffWorkflowException
from .base import Serializer, spec_map, op_map

# Create a list of tag names out of the spec names.
_spec_map = spec_map()
_op_map = op_map()


class XMLParserExcetion(SpiffWorkflowException):
    pass


class XmlSerializer(Serializer):
    """Parses XML into a WorkflowSpec object."""

    # Note: This is not a serializer.  It is a parser for Spiff's XML format
    # However, it is too disruptive to rename everything that uses it.

    def raise_parser_exception(self, message):
        raise XMLParserExcetion(message)

    def deserialize_assign(self, workflow, start_node):
        """
        Reads the "pre-assign" or "post-assign" tag from the given node.

        start_node -- the xml node (xml.dom.minidom.Node)
        """
        name = start_node.attrib.get('name')
        attrib = start_node.attrib.get('field')
        value = start_node.attrib.get('value')

        kwargs = {}
        if name == '':
            self.raise_parser_exception('name attribute required')
        if attrib is not None and value is not None:
            self.raise_parser_exception('Both, field and right-value attributes found')
        elif attrib is None and value is None:
            self.raise_parser_exception('field or value attribute required')
        elif value is not None:
            kwargs['right'] = value
        else:
            kwargs['right_attribute'] = attrib
        return operators.Assign(name, **kwargs)

    def deserialize_data(self, workflow, start_node):
        """
        Reads a "data" or "define" tag from the given node.

        start_node -- the xml node (xml.dom.minidom.Node)
        """
        name = start_node.attrib.get('name')
        value = start_node.attrib.get('value')
        return name, value

    def deserialize_assign_list(self, workflow, start_node):
        """
        Reads a list of assignments from the given node.

        workflow -- the workflow
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        # Collect all information.
        assignments = []
        for node in start_node.getchildren():
            if not isinstance(start_node.tag, str):
                pass
            elif node.tag.lower() == 'assign':
                assignments.append(self.deserialize_assign(workflow, node))
            else:
                self.raise_parser_exception('Unknown node: %s' % node.tag)
        return assignments

    def deserialize_logical(self, node):
        """
        Reads the logical tag from the given node, returns a Condition object.

        node -- the xml node (xml.dom.minidom.Node)
        """
        term1_attrib = node.attrib.get('left-field')
        term1_value = node.attrib.get('left-value')
        op = node.tag.lower()
        term2_attrib = node.attrib.get('right-field')
        term2_value = node.attrib.get('right-value')
        if op not in _op_map:
            self.raise_parser_exception('Invalid operator')
        if term1_attrib is not None and term1_value is not None:
            self.raise_parser_exception('Both, left-field and left-value attributes found')
        elif term1_attrib is None and term1_value is None:
            self.raise_parser_exception('left-field or left-value attribute required')
        elif term1_value is not None:
            left = term1_value
        else:
            left = operators.Attrib(term1_attrib)
        if term2_attrib is not None and term2_value is not None:
            self.raise_parser_exception('Both, right-field and right-value attributes found')
        elif term2_attrib is None and term2_value is None:
            self.raise_parser_exception('right-field or right-value attribute required')
        elif term2_value is not None:
            right = term2_value
        else:
            right = operators.Attrib(term2_attrib)
        return _op_map[op](left, right)

    def deserialize_condition(self, workflow, start_node):
        """
        Reads the conditional statement from the given node.

        workflow -- the workflow with which the concurrence is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        # Collect all information.
        condition = None
        spec_name = None
        for node in start_node.getchildren():
            if not isinstance(node.tag, str):
                pass
            elif node.tag.lower() == 'successor':
                if spec_name is not None:
                    self.raise_parser_exception('Duplicate task name %s' % spec_name)
                if node.text is None:
                    self.raise_parser_exception('Successor tag without a task name')
                spec_name = node.text
            elif node.tag.lower() in _op_map:
                if condition is not None:
                    self.raise_parser_exception('Multiple conditions are not yet supported')
                condition = self.deserialize_logical(node)
            else:
                self.raise_parser_exception('Unknown node: %s' % node.tag)

        if condition is None:
            self.raise_parser_exception('Missing condition in conditional statement')
        if spec_name is None:
            self.raise_parser_exception('A %s has no task specified' % start_node.tag)
        return condition, spec_name

    def deserialize_task_spec(self, workflow, start_node, read_specs):
        """
        Reads the task from the given node and returns a tuple
        (start, end) that contains the stream of objects that model
        the behavior.

        workflow -- the workflow with which the task is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        # Extract attributes from the node.
        nodetype = start_node.tag.lower()
        name = start_node.attrib.get('name', '').lower()
        context = start_node.attrib.get('context', '').lower()
        mutex = start_node.attrib.get('mutex', '').lower()
        cancel = start_node.attrib.get('cancel', '').lower()
        success = start_node.attrib.get('success', '').lower()
        times = start_node.attrib.get('times', '').lower()
        times_field = start_node.attrib.get('times-field', '').lower()
        threshold = start_node.attrib.get('threshold', '').lower()
        threshold_field = start_node.attrib.get('threshold-field', '').lower()
        file_name = start_node.attrib.get('file', '').lower()
        file_field = start_node.attrib.get('file-field', '').lower()
        kwargs = {'data':        {},
                  'defines':     {},
                  'pre_assign':  [],
                  'post_assign': []}
        if nodetype not in _spec_map:
            self.raise_parser_exception('Invalid task type "%s"' % nodetype)
        if nodetype == 'start-task':
            name = 'start'
        if name == '':
            self.raise_parser_exception('Invalid task name "%s"' % name)
        if name in read_specs:
            self.raise_parser_exception('Duplicate task name "%s"' % name)
        if cancel != '' and cancel != '0':
            kwargs['cancel'] = True
        if success != '' and success != '0':
            kwargs['success'] = True
        if times != '':
            kwargs['times'] = int(times)
        if times_field != '':
            kwargs['times'] = operators.Attrib(times_field)
        if threshold != '':
            kwargs['threshold'] = int(threshold)
        if threshold_field != '':
            kwargs['threshold'] = operators.Attrib(threshold_field)
        if file_name != '':
            kwargs['file'] = file_name
        if file_field != '':
            kwargs['file'] = operators.Attrib(file_field)
        if nodetype == 'choose':
            kwargs['choice'] = []
        if nodetype == 'trigger':
            context = [context]
        if mutex != '':
            context = mutex

        # Walk through the children of the node.
        successors = []
        for node in start_node.getchildren():
            if not isinstance(node.tag, str):
                pass
            elif node.tag == 'description':
                kwargs['description'] = node.text
            elif node.tag == 'successor' \
                    or node.tag == 'default-successor':
                if not node.text:
                    self.raise_parser_exception('Empty %s tag' % node.tag)
                successors.append((None, node.text))
            elif node.tag == 'conditional-successor':
                successors.append(self.deserialize_condition(workflow, node))
            elif node.tag == 'define':
                key, value = self.deserialize_data(workflow, node)
                kwargs['defines'][key] = value
            # "property" tag exists for backward compatibility.
            elif node.tag == 'data' or node.tag == 'property':
                key, value = self.deserialize_data(workflow, node)
                kwargs['data'][key] = value
            elif node.tag == 'pre-assign':
                kwargs['pre_assign'].append(
                    self.deserialize_assign(workflow, node))
            elif node.tag == 'post-assign':
                kwargs['post_assign'].append(
                    self.deserialize_assign(workflow, node))
            elif node.tag == 'in':
                kwargs['in_assign'] = self.deserialize_assign_list(
                    workflow, node)
            elif node.tag == 'out':
                kwargs['out_assign'] = self.deserialize_assign_list(
                    workflow, node)
            elif node.tag == 'cancel':
                if not node.text:
                    self.raise_parser_exception('Empty %s tag' % node.tag)
                if context == '':
                    context = []
                elif not isinstance(context, list):
                    context = [context]
                context.append(node.text)
            elif node.tag == 'pick':
                if not node.text:
                    self.raise_parser_exception('Empty %s tag' % node.tag)
                kwargs['choice'].append(node.text)
            else:
                self.raise_parser_exception('Unknown node: %s' % node.tag)

        # Create a new instance of the task spec.
        module = _spec_map[nodetype]
        if nodetype == 'start-task':
            spec = module(workflow, **kwargs)
        elif nodetype == 'multi-instance' or nodetype == 'thread-split':
            if times == '' and times_field == '':
                self.raise_parser_exception('Missing "times" or "times-field" in "%s"' % name)
            elif times != '' and times_field != '':
                self.raise_parser_exception('Both, "times" and "times-field" in "%s"' % name)
            spec = module(workflow, name, **kwargs)
        elif context == '':
            spec = module(workflow, name, **kwargs)
        else:
            spec = module(workflow, name, context, **kwargs)

        read_specs[name] = spec, successors

    def deserialize_workflow_spec(self, root_node, filename=None):
        """
        Reads the workflow from the given XML structure and returns a
        WorkflowSpec instance.
        """
        name = root_node.attrib.get('name')
        if name == '':
            self.raise_parser_exception('%s without a name attribute' % root_node.tag)

        # Read all task specs and create a list of successors.
        workflow_spec = WorkflowSpec(name, filename)
        del workflow_spec.task_specs['Start']
        end = Simple(workflow_spec, 'End'), []
        read_specs = dict(end=end)
        for child_node in root_node.getchildren():
            if not isinstance(child_node.tag, str):
                pass
            elif child_node.tag == 'name':
                workflow_spec.name = child_node.text
            elif child_node.tag == 'description':
                workflow_spec.description = child_node.text
            elif child_node.tag.lower() in _spec_map:
                self.deserialize_task_spec(workflow_spec, child_node, read_specs)
            else:
                self.raise_parser_exception('Unknown node: %s' % child_node.tag)

        # Remove the default start-task from the workflow.
        workflow_spec.start = read_specs['start'][0]

        # Connect all task specs.
        for name in read_specs:
            spec, successors = read_specs[name]
            for condition, successor_name in successors:
                if successor_name not in read_specs:
                    self.raise_parser_exception('Unknown successor: "%s"' % successor_name)
                successor, foo = read_specs[successor_name]
                if condition is None:
                    spec.connect(successor)
                else:
                    spec.connect_if(condition, successor)
        return workflow_spec
