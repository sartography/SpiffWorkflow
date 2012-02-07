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
import os, sys
import xml.dom.minidom as minidom
import SpiffWorkflow
import SpiffWorkflow.Tasks
from SpiffWorkflow import operators
from SpiffWorkflow.Exception import StorageException

class OpenWfeXmlReader(object):
    """
    Parses OpenWFE XML into a workflow object.
    """

    def __init__(self):
        """
        Constructor.
        """
        self.task_tags = ('task',
                          'concurrence',
                          'if',
                          'sequence')
        self.op_map = {'equals':       operators.Equal,
                       'not-equals':   operators.NotEqual,
                       'less-than':    operators.LessThan,
                       'greater-than': operators.GreaterThan,
                       'matches':      operators.Match}


    def _raise(self, error):
        raise StorageException('%s in XML file.' % error)


    def read_condition(self, node):
        """
        Reads the logical tag from the given node, returns a Condition object.
        
        node -- the xml node (xml.dom.minidom.Node)
        """
        term1 = node.getAttribute('field-value')
        op    = node.nodeName.lower()
        term2 = node.getAttribute('other-value')
        if not self.op_map.has_key(op):
            self._raise('Invalid operator')
        return self.op_map[op](operators.Attrib(term1),
                               operators.Attrib(term2))


    def read_if(self, workflow, start_node):
        """
        Reads the sequence from the given node.
        
        workflow -- the workflow with which the concurrence is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        assert start_node.nodeName.lower() == 'if'
        name = start_node.getAttribute('name').lower()

        # Collect all information.
        match     = None
        nomatch   = None
        condition = None
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName.lower() in self.task_tags:
                if match is None:
                    match = self.read_task(workflow, node)
                elif nomatch is None:
                    nomatch = self.read_task(workflow, node)
                else:
                    assert False # Only two tasks in "if" allowed.
            elif node.nodeName.lower() in self.op_map:
                if condition is None:
                    condition = self.read_condition(node)
                else:
                    assert False # Multiple conditions not yet supported.
            else:
                print "Unknown type:", type
                assert False # Unknown tag.

        # Model the if statement.
        assert condition is not None
        assert match     is not None
        choice = SpiffWorkflow.Tasks.ExclusiveChoice(workflow, name)
        end    = SpiffWorkflow.Tasks.Simple(workflow, name + '_end')
        if nomatch is None:
            choice.connect(end)
        else:
            choice.connect(nomatch[0])
            nomatch[1].connect(end)
        choice.connect_if(condition, match[0])
        match[1].connect(end)

        return (choice, end)


    def read_sequence(self, workflow, start_node):
        """
        Reads the children of the given node in sequential order.
        Returns a tuple (start, end) that contains the stream of objects
        that model the behavior.
        
        workflow -- the workflow with which the concurrence is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        assert start_node.nodeName.lower() == 'sequence'
        name  = start_node.getAttribute('name').lower()
        first = None
        last  = None
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName.lower() in self.task_tags:
                (start, end) = self.read_task(workflow, node)
                if first is None:
                    first = start
                else:
                    last.connect(start)
                last = end
            else:
                print "Unknown type:", type
                assert False # Unknown tag.
        return (first, last)


    def read_concurrence(self, workflow, start_node):
        """
        Reads the concurrence from the given node.
        
        workflow -- the workflow with which the concurrence is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        assert start_node.nodeName.lower() == 'concurrence'
        name = start_node.getAttribute('name').lower()
        multichoice = SpiffWorkflow.Tasks.MultiChoice(workflow, name)
        synchronize = SpiffWorkflow.Tasks.Join(workflow, name + '_end', name)
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName.lower() in self.task_tags:
                (start, end) = self.read_task(workflow, node)
                multichoice.connect_if(None, start)
                end.connect(synchronize)
            else:
                print "Unknown type:", type
                assert False # Unknown tag.
        return (multichoice, synchronize)


    def read_task(self, workflow, start_node):
        """
        Reads the task from the given node and returns a tuple
        (start, end) that contains the stream of objects that model
        the behavior.
        
        workflow -- the workflow with which the task is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        type = start_node.nodeName.lower()
        name = start_node.getAttribute('name').lower()
        assert type in self.task_tags

        if type == 'concurrence':
            return self.read_concurrence(workflow, start_node)
        elif type == 'if':
            return self.read_if(workflow, start_node)
        elif type == 'sequence':
            return self.read_sequence(workflow, start_node)
        elif type == 'task':
            task = SpiffWorkflow.Tasks.Simple(workflow, name)
            return (task, task)
        else:
            print "Unknown type:", type
            assert False # Unknown tag.


    def read_workflow(self, start_node):
        """
        Reads the workflow from the given workflow node and returns a workflow
        object.
        
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        name = start_node.getAttribute('name')
        assert name is not None
        workflow  = SpiffWorkflow.Workflow(name)
        last_task = workflow.start
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName == 'description':
                pass
            elif node.nodeName.lower() in self.task_tags:
                (start, end) = self.read_task(workflow, node)
                last_task.connect(start)
                last_task = end
            else:
                print "Unknown type:", type
                assert False # Unknown tag.

        last_task.connect(SpiffWorkflow.Tasks.Simple(workflow, 'End'))
        return workflow


    def read(self, xml):
        """
        Reads all workflows from the given XML structure and returns a
        list of workflow object.
        
        xml -- the xml structure (xml.dom.minidom.Node)
        """
        workflows = []
        for node in xml.getElementsByTagName('process-definition'):
            workflows.append(self.read_workflow(node))
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
        return self.read(minidom.parse(filename))
