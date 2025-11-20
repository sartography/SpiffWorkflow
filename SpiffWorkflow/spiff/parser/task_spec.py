# Copyright (C) 2023 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

from lxml import etree

from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser
from SpiffWorkflow.bpmn.parser.task_parsers import SubprocessParser
from SpiffWorkflow.bpmn.parser.util import xpath_eval

from SpiffWorkflow.spiff.specs.defaults import (
    StandardLoopTask,
    ParallelMultiInstanceTask,
    SequentialMultiInstanceTask,
    BusinessRuleTask,
    UserTask,
)

SPIFFWORKFLOW_NSMAP = {'spiffworkflow': 'http://spiffworkflow.org/bpmn/schema/1.0/core'}


class SpiffTaskParser(TaskParser):

    STANDARD_LOOP_CLASS = StandardLoopTask
    PARALLEL_MI_CLASS = ParallelMultiInstanceTask
    SEQUENTIAL_MI_CLASS = SequentialMultiInstanceTask

    def parse_extensions(self, node=None):
        if node is None:
            node = self.node
        return SpiffTaskParser._parse_extensions(node)

    @staticmethod
    def _parse_extensions(node):
        # Too bad doing this works in such a stupid way.
        # We should set a namespace and automatically do this.
        extensions = {}
        xpath = xpath_eval(node, SPIFFWORKFLOW_NSMAP)
        extension_nodes = xpath(f'./bpmn:extensionElements/spiffworkflow:*')
        for node in extension_nodes:
            name = etree.QName(node).localname
            if name == 'properties':
                extensions['properties'] = SpiffTaskParser._parse_properties(node)
            elif name == 'unitTests':
                extensions['unitTests'] = SpiffTaskParser._parse_script_unit_tests(node)
            elif name == 'serviceTaskOperator':
                extensions['serviceTaskOperator'] = SpiffTaskParser._parse_servicetask_operator(node)
            elif name == 'taskMetadataValues':
                extensions['taskMetadataValues'] = SpiffTaskParser._parse_task_metadata_values(node)
            else:
                extensions[name] = node.text
        return extensions

    @classmethod
    def _node_children_by_tag_name(cls, node, tag_name):
        xpath = cls._spiffworkflow_ready_xpath_for_node(node)
        return xpath(f'.//spiffworkflow:{tag_name}')

    @classmethod
    def _parse_properties(cls, node):
        property_nodes = cls._node_children_by_tag_name(node, 'property')
        properties = {}
        for prop_node in property_nodes:
            properties[prop_node.attrib['name']] = prop_node.attrib['value']
        return properties

    @classmethod
    def _parse_task_metadata_values(cls, node):
        metadata_value_nodes = cls._node_children_by_tag_name(node, 'taskMetadataValue')
        metadata_values = {}
        for metadata_node in metadata_value_nodes:
            metadata_values[metadata_node.attrib['name']] = metadata_node.attrib['value']
        return metadata_values

    @staticmethod
    def _spiffworkflow_ready_xpath_for_node(node):
        return xpath_eval(node, SPIFFWORKFLOW_NSMAP)

    @classmethod
    def _parse_script_unit_tests(cls, node):
        unit_test_nodes = cls._node_children_by_tag_name(node, 'unitTest')
        unit_tests = []
        for unit_test_node in unit_test_nodes:
            unit_test_dict = {"id": unit_test_node.attrib['id']}
            unit_test_dict['inputJson'] = cls._node_children_by_tag_name(unit_test_node, 'inputJson')[0].text
            unit_test_dict['expectedOutputJson'] = cls._node_children_by_tag_name(unit_test_node, 'expectedOutputJson')[0].text
            unit_tests.append(unit_test_dict)
        return unit_tests

    @classmethod
    def _parse_servicetask_operator(cls, node):
        name = node.attrib['id']
        result_variable = node.get('resultVariable', None)
        parameter_nodes = cls._node_children_by_tag_name(node, 'parameter')
        operator = {'name': name, 'resultVariable': result_variable}
        parameters = {}
        for param_node in parameter_nodes:
            if 'value' in param_node.attrib:
                parameters[param_node.attrib['id']] = {
                    'value': param_node.attrib['value'],
                    'type': param_node.attrib['type']
                }
        operator['parameters'] = parameters
        return operator

    def _copy_task_attrs(self, original, loop_characteristics):
        # I am so disappointed I have to do this.
        super()._copy_task_attrs(original)
        if loop_characteristics.xpath('@spiffworkflow:scriptsOnInstances', namespaces=SPIFFWORKFLOW_NSMAP) != ['true']:
            self.task.prescript = original.prescript
            self.task.postscript = original.postscript
            original.prescript = None
            original.postscript = None

    def create_task(self):
        # The main task parser already calls this, and even sets an attribute, but
        # 1. It calls it after creating the task so I don't have access to it here yet and
        # 2. I want defined attributes, not a dict of random crap
        # (though the dict of random crap will still be there since the base parser adds it).
        extensions = self.parse_extensions()
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        return self.spec_class(self.spec, self.bpmn_id, prescript=prescript, postscript=postscript, **self.bpmn_attributes)


class SubWorkflowParser(SpiffTaskParser):

    def create_task(self):
        extensions = self.parse_extensions()
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        subworkflow_spec = SubprocessParser.get_subprocess_spec(self)
        return self.spec_class(
            self.spec, 
            self.bpmn_id,
            subworkflow_spec=subworkflow_spec,
            prescript=prescript,
            postscript=postscript,
            **self.bpmn_attributes)


class ScriptTaskParser(SpiffTaskParser):
    def create_task(self):
        script = None
        for child_node in self.node:
            if child_node.tag.endswith('script'):
                script = child_node.text
        return self.spec_class(self.spec, self.bpmn_id, script, **self.bpmn_attributes)


class CallActivityParser(SpiffTaskParser):

    def create_task(self):
        extensions = self.parse_extensions()
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        subworkflow_spec = SubprocessParser.get_call_activity_spec(self)
        return self.spec_class(
            self.spec, 
            self.bpmn_id,
            subworkflow_spec=subworkflow_spec,
            prescript=prescript,
            postscript=postscript,
            **self.bpmn_attributes)

class ServiceTaskParser(SpiffTaskParser):
    def create_task(self):
        extensions = self.parse_extensions()
        operator = extensions.get('serviceTaskOperator')
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        return self.spec_class(
                self.spec,
                self.bpmn_id,
                operation_name=operator['name'], 
                operation_params=operator['parameters'],
                result_variable=operator['resultVariable'],
                prescript=prescript,
                postscript=postscript,
                **self.bpmn_attributes)

class BusinessRuleTaskParser(SpiffTaskParser):

    def create_task(self):
        decision_ref = self.get_decision_ref(self.node)
        extensions = self.parse_extensions()
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        return BusinessRuleTask(
            self.spec,
            self.bpmn_id,
            dmnEngine=self.process_parser.parser.get_engine(decision_ref, self.node),
            prescript=prescript,
            postscript=postscript,
            **self.bpmn_attributes,
        )

    @staticmethod
    def get_decision_ref(node):
        extensions = SpiffTaskParser._parse_extensions(node)
        return extensions.get('calledDecisionId')

class UserTaskParser(SpiffTaskParser):

    def create_task(self):
        extensions = self.parse_extensions()
        variable = extensions.get('variableName')
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        return UserTask(
            self.spec,
            self.bpmn_id,
            variable=variable,
            prescript=prescript,
            postscript=postscript,
            **self.bpmn_attributes,
        )

