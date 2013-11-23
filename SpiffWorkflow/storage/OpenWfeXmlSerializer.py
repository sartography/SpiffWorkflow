# -*- coding: utf-8 -*-
from __future__ import division
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
import os
import sys
import xml.dom.minidom as minidom
from SpiffWorkflow import operators, specs
from SpiffWorkflow.exceptions import StorageException
from SpiffWorkflow.storage.Serializer import Serializer

_spec_tags = ('task',
              'concurrence',
              'if',
              'sequence')
_op_map = {'equals':       operators.Equal,
           'not-equals':   operators.NotEqual,
           'less-than':    operators.LessThan,
           'greater-than': operators.GreaterThan,
           'matches':      operators.Match}

class OpenWfeXmlSerializer(Serializer):
    """
    Parses OpenWFE XML into a workflow object.
    """
    def _read_condition(self, node):
        """
        Reads the logical tag from the given node, returns a Condition object.

        node -- the xml node (xml.dom.minidom.Node)
        """
        term1 = node.getAttribute('field-value')
        op    = node.nodeName.lower()
        term2 = node.getAttribute('other-value')
        if op not in _op_map:
            raise StorageException('Invalid operator in XML file')
        return _op_map[op](operators.Attrib(term1),
                           operators.Attrib(term2))

    def _read_if(self, workflow, start_node):
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
            if node.nodeName.lower() in _spec_tags:
                if match is None:
                    match = self._read_spec(workflow, node)
                elif nomatch is None:
                    nomatch = self._read_spec(workflow, node)
                else:
                    assert False # Only two tasks in "if" allowed.
            elif node.nodeName.lower() in _op_map:
                if condition is None:
                    condition = self._read_condition(node)
                else:
                    assert False # Multiple conditions not yet supported.
            else:
                print("Unknown type:", type)
                assert False # Unknown tag.

        # Model the if statement.
        assert condition is not None
        assert match     is not None
        choice = specs.ExclusiveChoice(workflow, name)
        end    = specs.Simple(workflow, name + '_end')
        if nomatch is None:
            choice.connect(end)
        else:
            choice.connect(nomatch[0])
            nomatch[1].connect(end)
        choice.connect_if(condition, match[0])
        match[1].connect(end)

        return (choice, end)

    def _read_sequence(self, workflow, start_node):
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
            if node.nodeName.lower() in _spec_tags:
                (start, end) = self._read_spec(workflow, node)
                if first is None:
                    first = start
                else:
                    last.connect(start)
                last = end
            else:
                print("Unknown type:", type)
                assert False # Unknown tag.
        return (first, last)

    def _read_concurrence(self, workflow, start_node):
        """
        Reads the concurrence from the given node.

        workflow -- the workflow with which the concurrence is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        assert start_node.nodeName.lower() == 'concurrence'
        name = start_node.getAttribute('name').lower()
        multichoice = specs.MultiChoice(workflow, name)
        synchronize = specs.Join(workflow, name + '_end', name)
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName.lower() in _spec_tags:
                (start, end) = self._read_spec(workflow, node)
                multichoice.connect_if(None, start)
                end.connect(synchronize)
            else:
                print("Unknown type:", type)
                assert False # Unknown tag.
        return (multichoice, synchronize)

    def _read_spec(self, workflow, start_node):
        """
        Reads the task spec from the given node and returns a tuple
        (start, end) that contains the stream of objects that model
        the behavior.

        workflow -- the workflow with which the task spec is associated
        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        type = start_node.nodeName.lower()
        name = start_node.getAttribute('name').lower()
        assert type in _spec_tags

        if type == 'concurrence':
            return self._read_concurrence(workflow, start_node)
        elif type == 'if':
            return self._read_if(workflow, start_node)
        elif type == 'sequence':
            return self._read_sequence(workflow, start_node)
        elif type == 'task':
            spec = specs.Simple(workflow, name)
            return spec, spec
        else:
            print("Unknown type:", type)
            assert False # Unknown tag.

    def _read_workflow(self, start_node):
        """
        Reads the workflow specification from the given workflow node
        and returns a list of WorkflowSpec objects.

        start_node -- the xml structure (xml.dom.minidom.Node)
        """
        name = start_node.getAttribute('name')
        assert name is not None
        workflow_spec = specs.WorkflowSpec(name)
        last_spec     = workflow_spec.start
        for node in start_node.childNodes:
            if node.nodeType != minidom.Node.ELEMENT_NODE:
                continue
            if node.nodeName == 'description':
                pass
            elif node.nodeName.lower() in _spec_tags:
                (start, end) = self._read_spec(workflow_spec, node)
                last_spec.connect(start)
                last_spec = end
            else:
                print("Unknown type:", type)
                assert False # Unknown tag.

        last_spec.connect(specs.Simple(workflow_spec, 'End'))
        return workflow_spec

    def deserialize_workflow_spec(self, s_state, **kwargs):
        """
        Reads the workflow from the given XML structure and returns a
        workflow object.
        """
        dom  = minidom.parseString(s_state)
        node = dom.getElementsByTagName('process-definition')[0]
        return self._read_workflow(node)
