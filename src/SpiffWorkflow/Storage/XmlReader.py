# Copyright (C) 2007 Samuel Abels
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
import os, re
import xml.dom.minidom as minidom
import SpiffWorkflow
import SpiffWorkflow.Tasks
import SpiffWorkflow.Operators
from SpiffWorkflow.Exception import StorageException

class XmlReader(object):
    """
    Parses XML into a workflow object.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.read_tasks = {}

        # Create a list of tag names out of the task names.
        self.task_map = {}
        for name in dir(SpiffWorkflow.Tasks):
            if name.startswith('_'):
                continue
            module = SpiffWorkflow.Tasks.__dict__[name]
            name   = re.sub(r'(.)([A-Z])', r'\1-\2', name).lower()
            self.task_map[name] = module

        self.op_map = {'equals':       SpiffWorkflow.Operators.Equal,
                       'not-equals':   SpiffWorkflow.Operators.NotEqual,
                       'less-than':    SpiffWorkflow.Operators.LessThan,
                       'greater-than': SpiffWorkflow.Operators.GreaterThan,
                       'matches':      SpiffWorkflow.Operators.Match}


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
        return SpiffWorkflow.Tasks.Assign(name, **kwargs)


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
        if not self.op_map.has_key(op):
            self._raise('Invalid operator')
        if term1_attrib != '' and term1_value != '':
            self._raise('Both, left-field and left-value attributes found')
        elif term1_attrib == '' and term1_value == '':
            self._raise('left-field or left-value attribute required')
        elif term1_value != '':
            left = term1_value
        else:
            left = SpiffWorkflow.Operators.Attrib(term1_attrib)
        if term2_attrib != '' and term2_value != '':
            self._raise('Both, right-field and right-value attributes found')
        elif term2_attrib == '' and term2_value == '':
            self._raise('right-field or right-value attribute required')
        elif term2_value != '':
            right = term2_value
        else:
            right = SpiffWorkflow.Operators.Attrib(term2_attrib)
        return self.op_map[op](left, right)


    def _read_condition(self, workflow, start_node):
        """
        Reads the conditional statement from the given node.
        
        workflow -- the workflow with which the concurrence is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        # Collect all information.
        condition = None
        task_name = None
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName.lower() == 'successor':
                if task_name is not None:
                    self._raise('Duplicate task name %s' % task_name)
                if node.firstChild is None:
                    self._raise('Successor tag without a task name')
                task_name = node.firstChild.nodeValue
            elif node.nodeName.lower() in self.op_map:
                if condition is not None:
                    self._raise('Multiple conditions are not yet supported')
                condition = self._read_logical(node)
            else:
                self._raise('Unknown node: %s' % node.nodeName)

        if condition is None:
            self._raise('Missing condition in conditional statement')
        if task_name is None:
            self._raise('A %s has no task specified' % start_node.nodeName)
        return (condition, task_name)


    def read_task(self, workflow, start_node):
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
        if not self.task_map.has_key(nodetype):
            self._raise('Invalid task type "%s"' % nodetype)
        if nodetype == 'start-task':
            name = 'start'
        if name == '':
            self._raise('Invalid task name "%s"' % name)
        if self.read_tasks.has_key(name):
            self._raise('Duplicate task name "%s"' % name)
        if cancel != '' and cancel != u'0':
            kwargs['cancel'] = True
        if success != '' and success != u'0':
            kwargs['success'] = True
        if times != '':
            kwargs['times'] = int(times)
        if times_field != '':
            kwargs['times'] = SpiffWorkflow.Operators.Attrib(times_field)
        if threshold != '':
            kwargs['threshold'] = int(threshold)
        if threshold_field != '':
            kwargs['threshold'] = SpiffWorkflow.Operators.Attrib(threshold_field)
        if file != '':
            kwargs['file'] = file
        if file_field != '':
            kwargs['file'] = SpiffWorkflow.Operators.Attrib(file_field)
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

        # Create a new instance of the task.
        module = self.task_map[nodetype]
        if nodetype == 'start-task':
            task = module(workflow, **kwargs)
        elif nodetype == 'multi-instance' or nodetype == 'thread-split':
            if times == '' and times_field == '':
                self._raise('Missing "times" or "times-field" in "%s"' % name)
            elif times != '' and times_field != '':
                self._raise('Both, "times" and "times-field" in "%s"' % name)
            task  = module(workflow, name, **kwargs)
        elif context == '':
            task = module(workflow, name, **kwargs)
        else:
            task = module(workflow, name, context, **kwargs)

        self.read_tasks[name] = (task, successors)


    def _read_workflow(self, start_node, filename = None):
        """
        Reads the workflow from the given workflow node and returns a workflow
        object.
        
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        name = start_node.getAttribute('name')
        if name == '':
            self._raise('%s without a name attribute' % start_node.nodeName)

        # Read all tasks and create a list of successors.
        workflow             = SpiffWorkflow.Workflow(name, filename)
        self.read_tasks = {'end': (SpiffWorkflow.Tasks.Task(workflow, 'End'), [])}
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName == 'description':
                workflow.description = node.firstChild.nodeValue
            elif self.task_map.has_key(node.nodeName.lower()):
                self.read_task(workflow, node)
            else:
                self._raise('Unknown node: %s' % node.nodeName)

        # Remove the default start-task from the workflow.
        workflow.start = self.read_tasks['start'][0]

        # Connect all tasks.
        for name in self.read_tasks:
            task, successors = self.read_tasks[name]
            for condition, successor_name in successors:
                if not self.read_tasks.has_key(successor_name):
                    self._raise('Unknown successor: "%s"' % successor_name)
                successor, foo = self.read_tasks[successor_name]
                if condition is None:
                    task.connect(successor)
                else:
                    task.connect_if(condition, successor)
        return workflow


    def read(self, xml, filename = None):
        """
        Reads all workflows from the given XML structure and returns a
        list of workflow object.
        
        xml -- the xml structure (xml.dom.minidom.Node)
        """
        workflows = []
        for node in xml.getElementsByTagName('process-definition'):
            workflows.append(self._read_workflow(node, filename))
        return workflows


    def parse_string(self, string):
        """
        Reads the workflow XML from the given string and returns a workflow
        object.
        
        string -- the name of the file (string)
        """
        return self.read(minidom.parseString(string))


    def parse_file(self, filename):
        """
        Reads the workflow XML from the given file and returns a workflow
        object.
        
        filename -- the name of the file (string)
        """
        return self.read(minidom.parse(filename), filename)
