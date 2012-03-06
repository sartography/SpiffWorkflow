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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
import os
import re
import xml.dom.minidom as minidom
from SpiffWorkflow import operators, specs
from SpiffWorkflow.exceptions import StorageException
from SpiffWorkflow.storage.Serializer import Serializer

# Create a list of tag names out of the spec names.
_spec_map = dict()
for name in dir(specs):
    if name.startswith('_'):
        continue
    module = specs.__dict__[name]
    name   = re.sub(r'(.)([A-Z])', r'\1-\2', name).lower()
    _spec_map[name] = module
_spec_map['task'] = specs.Simple

_op_map = {'equals':       operators.Equal,
           'not-equals':   operators.NotEqual,
           'less-than':    operators.LessThan,
           'greater-than': operators.GreaterThan,
           'matches':      operators.Match}

class XmlSerializer(Serializer):
    """
    Parses XML into a WorkflowSpec object.
    """
    def _raise(self, error):
        raise StorageException('%s in XML file.' % error)

    def _read_assign(self, workflow, start_node):
        """
        Reads the "pre-assign" or "post-assign" tag from the given node.
        
        start_node -- the xml node (xml.dom.minidom.Node)
        """
        name   = start_node.getAttribute('name')
        attrib = start_node.getAttribute('field')
        value  = start_node.getAttribute('value')
        kwargs = {}
        if name == '':
            self._raise('name attribute required')
        if attrib != '' and value != '':
            self._raise('Both, field and right-value attributes found')
        elif attrib == '' and value == '':
            self._raise('field or value attribute required')
        elif value != '':
            kwargs['right'] = value
        else:
            kwargs['right_attribute'] = attrib
        return specs.Assign(name, **kwargs)

    def _read_property(self, workflow, start_node):
        """
        Reads a "property" or "define" tag from the given node.
        
        start_node -- the xml node (xml.dom.minidom.Node)
        """
        name   = start_node.getAttribute('name')
        value  = start_node.getAttribute('value')
        return name, value

    def _read_assign_list(self, workflow, start_node):
        """
        Reads a list of assignments from the given node.
        
        workflow -- the workflow
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        # Collect all information.
        assignments = []
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName.lower() == 'assign':
                assignments.append(self._read_assign(workflow, node))
            else:
                self._raise('Unknown node: %s' % node.nodeName)
        return assignments

    def _read_logical(self, node):
        """
        Reads the logical tag from the given node, returns a Condition object.
        
        node -- the xml node (xml.dom.minidom.Node)
        """
        term1_attrib = node.getAttribute('left-field')
        term1_value  = node.getAttribute('left-value')
        op           = node.nodeName.lower()
        term2_attrib = node.getAttribute('right-field')
        term2_value  = node.getAttribute('right-value')
        kwargs       = {}
        if not _op_map.has_key(op):
            self._raise('Invalid operator')
        if term1_attrib != '' and term1_value != '':
            self._raise('Both, left-field and left-value attributes found')
        elif term1_attrib == '' and term1_value == '':
            self._raise('left-field or left-value attribute required')
        elif term1_value != '':
            left = term1_value
        else:
            left = operators.Attrib(term1_attrib)
        if term2_attrib != '' and term2_value != '':
            self._raise('Both, right-field and right-value attributes found')
        elif term2_attrib == '' and term2_value == '':
            self._raise('right-field or right-value attribute required')
        elif term2_value != '':
            right = term2_value
        else:
            right = operators.Attrib(term2_attrib)
        return _op_map[op](left, right)

    def _read_condition(self, workflow, start_node):
        """
        Reads the conditional statement from the given node.
        
        workflow -- the workflow with which the concurrence is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        # Collect all information.
        condition = None
        spec_name = None
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName.lower() == 'successor':
                if spec_name is not None:
                    self._raise('Duplicate task name %s' % spec_name)
                if node.firstChild is None:
                    self._raise('Successor tag without a task name')
                spec_name = node.firstChild.nodeValue
            elif node.nodeName.lower() in _op_map:
                if condition is not None:
                    self._raise('Multiple conditions are not yet supported')
                condition = self._read_logical(node)
            else:
                self._raise('Unknown node: %s' % node.nodeName)

        if condition is None:
            self._raise('Missing condition in conditional statement')
        if spec_name is None:
            self._raise('A %s has no task specified' % start_node.nodeName)
        return condition, spec_name

    def _deserialize_task_spec(self, workflow, start_node, read_specs):
        """
        Reads the task from the given node and returns a tuple
        (start, end) that contains the stream of objects that model
        the behavior.
        
        workflow -- the workflow with which the task is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        # Extract attributes from the node.
        nodetype        = start_node.nodeName.lower()
        name            = start_node.getAttribute('name').lower()
        context         = start_node.getAttribute('context').lower()
        mutex           = start_node.getAttribute('mutex').lower()
        cancel          = start_node.getAttribute('cancel').lower()
        success         = start_node.getAttribute('success').lower()
        times           = start_node.getAttribute('times').lower()
        times_field     = start_node.getAttribute('times-field').lower()
        threshold       = start_node.getAttribute('threshold').lower()
        threshold_field = start_node.getAttribute('threshold-field').lower()
        file            = start_node.getAttribute('file').lower()
        file_field      = start_node.getAttribute('file-field').lower()
        kwargs          = {'lock':        [],
                           'properties':  {},
                           'defines':     {},
                           'pre_assign':  [],
                           'post_assign': []}
        if not _spec_map.has_key(nodetype):
            self._raise('Invalid task type "%s"' % nodetype)
        if nodetype == 'start-task':
            name = 'start'
        if name == '':
            self._raise('Invalid task name "%s"' % name)
        if read_specs.has_key(name):
            self._raise('Duplicate task name "%s"' % name)
        if cancel != '' and cancel != u'0':
            kwargs['cancel'] = True
        if success != '' and success != u'0':
            kwargs['success'] = True
        if times != '':
            kwargs['times'] = int(times)
        if times_field != '':
            kwargs['times'] = operators.Attrib(times_field)
        if threshold != '':
            kwargs['threshold'] = int(threshold)
        if threshold_field != '':
            kwargs['threshold'] = operators.Attrib(threshold_field)
        if file != '':
            kwargs['file'] = file
        if file_field != '':
            kwargs['file'] = operators.Attrib(file_field)
        if nodetype == 'choose':
            kwargs['choice'] = []
        if nodetype == 'trigger':
            context = [context]
        if mutex != '':
            context = mutex

        # Walk through the children of the node.
        successors  = []
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName == 'description':
                kwargs['description'] = node.firstChild.nodeValue
            elif node.nodeName == 'successor' \
              or node.nodeName == 'default-successor':
                if node.firstChild is None:
                    self._raise('Empty %s tag' % node.nodeName)
                successors.append((None, node.firstChild.nodeValue))
            elif node.nodeName == 'conditional-successor':
                successors.append(self._read_condition(workflow, node))
            elif node.nodeName == 'define':
                key, value = self._read_property(workflow, node)
                kwargs['defines'][key] = value
            elif node.nodeName == 'property':
                key, value = self._read_property(workflow, node)
                kwargs['properties'][key] = value
            elif node.nodeName == 'pre-assign':
                kwargs['pre_assign'].append(self._read_assign(workflow, node))
            elif node.nodeName == 'post-assign':
                kwargs['post_assign'].append(self._read_assign(workflow, node))
            elif node.nodeName == 'in':
                kwargs['in_assign'] = self._read_assign_list(workflow, node)
            elif node.nodeName == 'out':
                kwargs['out_assign'] = self._read_assign_list(workflow, node)
            elif node.nodeName == 'cancel':
                if node.firstChild is None:
                    self._raise('Empty %s tag' % node.nodeName)
                if context == '':
                    context = []
                elif type(context) != type([]):
                    context = [context]
                context.append(node.firstChild.nodeValue)
            elif node.nodeName == 'lock':
                if node.firstChild is None:
                    self._raise('Empty %s tag' % node.nodeName)
                kwargs['lock'].append(node.firstChild.nodeValue)
            elif node.nodeName == 'pick':
                if node.firstChild is None:
                    self._raise('Empty %s tag' % node.nodeName)
                kwargs['choice'].append(node.firstChild.nodeValue)
            else:
                self._raise('Unknown node: %s' % node.nodeName)

        # Create a new instance of the task spec.
        module = _spec_map[nodetype]
        if nodetype == 'start-task':
            spec = module(workflow, **kwargs)
        elif nodetype == 'multi-instance' or nodetype == 'thread-split':
            if times == '' and times_field == '':
                self._raise('Missing "times" or "times-field" in "%s"' % name)
            elif times != '' and times_field != '':
                self._raise('Both, "times" and "times-field" in "%s"' % name)
            spec = module(workflow, name, **kwargs)
        elif context == '':
            spec = module(workflow, name, **kwargs)
        else:
            spec = module(workflow, name, context, **kwargs)

        read_specs[name] = spec, successors

    def _read_workflow(self, start_node, filename = None):
        """
        Reads the workflow from the given node and returns a WorkflowSpec
        instance.
        
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        name = start_node.getAttribute('name')
        if name == '':
            self._raise('%s without a name attribute' % start_node.nodeName)

        # Read all task specs and create a list of successors.
        workflow_spec = specs.WorkflowSpec(name, filename)
        end           = specs.Simple(workflow_spec, 'End'), []
        read_specs    = dict(end = end)
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName == 'description':
                workflow_spec.description = node.firstChild.nodeValue
            elif _spec_map.has_key(node.nodeName.lower()):
                self._deserialize_task_spec(workflow_spec, node, read_specs)
            else:
                self._raise('Unknown node: %s' % node.nodeName)

        # Remove the default start-task from the workflow.
        workflow_spec.start = read_specs['start'][0]

        # Connect all task specs.
        for name in read_specs:
            spec, successors = read_specs[name]
            for condition, successor_name in successors:
                if not read_specs.has_key(successor_name):
                    self._raise('Unknown successor: "%s"' % successor_name)
                successor, foo = read_specs[successor_name]
                if condition is None:
                    spec.connect(successor)
                else:
                    spec.connect_if(condition, successor)
        return workflow_spec

    def deserialize_workflow_spec(self, s_state, filename = None):
        """
        Reads the workflow from the given XML structure and returns a
        workflow object.
        """
        dom  = minidom.parseString(s_state)
        node = dom.getElementsByTagName('process-definition')[0]
        return self._read_workflow(node, filename)
