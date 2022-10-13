from lxml import etree

from SpiffWorkflow.dmn.specs.BusinessRuleTask import BusinessRuleTask
from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser
from SpiffWorkflow.bpmn.parser.task_parsers import SubprocessParser
from SpiffWorkflow.bpmn.parser.util import xpath_eval

SPIFFWORKFLOW_MODEL_NS = 'http://spiffworkflow.org/bpmn/schema/1.0/core'
SPIFFWORKFLOW_MODEL_PREFIX = 'spiffworkflow'


class SpiffTaskParser(TaskParser):

    def parse_extensions(self, node=None):
        if node is None:
            node = self.node
        return SpiffTaskParser._parse_extensions(node)

    @staticmethod
    def _parse_extensions(node):
        # Too bad doing this works in such a stupid way.
        # We should set a namespace and automatically do this.
        extensions = {}
        extra_ns = {SPIFFWORKFLOW_MODEL_PREFIX: SPIFFWORKFLOW_MODEL_NS}
        xpath = xpath_eval(node, extra_ns)
        extension_nodes = xpath(f'.//bpmn:extensionElements/{SPIFFWORKFLOW_MODEL_PREFIX}:*')
        for node in extension_nodes:
            name = etree.QName(node).localname
            if name == 'properties':
                extensions['properties'] = SpiffTaskParser._parse_properties(node)
            elif name == 'unitTests':
                extensions['unitTests'] = SpiffTaskParser._parse_script_unit_tests(node)
            elif name == 'serviceTaskOperator':
                extensions['serviceTaskOperator'] = SpiffTaskParser._parse_servicetask_operator(node)
            else:
                extensions[name] = node.text
        return extensions

    @classmethod
    def _node_children_by_tag_name(cls, node, tag_name):
        xpath = cls._spiffworkflow_ready_xpath_for_node(node)
        return xpath(f'.//{SPIFFWORKFLOW_MODEL_PREFIX}:{tag_name}')

    @classmethod
    def _parse_properties(cls, node):
        property_nodes = cls._node_children_by_tag_name(node, 'property')
        properties = {}
        for prop_node in property_nodes:
            properties[prop_node.attrib['name']] = prop_node.attrib['value']
        return properties

    @staticmethod
    def _spiffworkflow_ready_xpath_for_node(node):
        extra_ns = {SPIFFWORKFLOW_MODEL_PREFIX: SPIFFWORKFLOW_MODEL_NS}
        return xpath_eval(node, extra_ns)

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

    def create_task(self):
        # The main task parser already calls this, and even sets an attribute, but
        # 1. It calls it after creating the task so I don't have access to it here yet and
        # 2. I want defined attributes, not a dict of random crap
        # (though the dict of random crap will still be there since the base parser adds it).
        extensions = self.parse_extensions()
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        return self.spec_class(self.spec, self.get_task_spec_name(),
                               lane=self.lane,
                               description=self.node.get('name', None),
                               position=self.position,
                               prescript=prescript,
                               postscript=postscript)


class SubWorkflowParser(SpiffTaskParser):

    def create_task(self):
        extensions = self.parse_extensions()
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        subworkflow_spec = SubprocessParser.get_subprocess_spec(self)
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None),
            prescript=prescript,
            postscript=postscript)


class ScriptTaskParser(SpiffTaskParser):
    def create_task(self):
        script = None
        for child_node in self.node:
            if child_node.tag.endswith('script'):
                script = child_node.text
        return self.spec_class(
            self.spec, self.get_task_spec_name(), script,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None))


class CallActivityParser(SpiffTaskParser):

    def create_task(self):
        extensions = self.parse_extensions()
        prescript = extensions.get('preScript')
        postscript = extensions.get('postScript')
        subworkflow_spec = SubprocessParser.get_call_activity_spec(self)
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None),
            prescript=prescript,
            postscript=postscript)

class ServiceTaskParser(SpiffTaskParser):
    def create_task(self):
        extensions = self.parse_extensions()
        operator = extensions.get('serviceTaskOperator')
        return self.spec_class(
                self.spec, self.get_task_spec_name(),
                operator['name'], operator['parameters'],
                operator['resultVariable'],
                description=self.node.get('name', None),
                lane=self.lane, position=self.position)

class BusinessRuleTaskParser(SpiffTaskParser):

    def create_task(self):
        decision_ref = self.get_decision_ref(self.node)
        return BusinessRuleTask(self.spec,
                                self.get_task_spec_name(),
                                dmnEngine=self.process_parser.parser.get_engine(decision_ref, self.node),
                                lane=self.lane,
                                position=self.position,
                                description=self.node.get('name', None)
                                )

    @staticmethod
    def get_decision_ref(node):
        extensions = SpiffTaskParser._parse_extensions(node)
        return extensions.get('calledDecisionId')
