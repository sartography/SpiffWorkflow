from lxml import etree

from SpiffWorkflow.spiff.parser.task_spec import SpiffTaskParser
from SpiffWorkflow.bpmn.parser.util import xpath_eval
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.bpmn.parser.node_parser import DEFAULT_NSMAP
from .task_spec import CAMUNDA_MODEL_NS

CAMUNDA_MODEL_PREFIX = 'camunda'


class CallActivitySubprocessParser:
    """Parses a CallActivity node."""

    @staticmethod
    def get_subprocess_spec(task_parser):
        workflow_start_event = task_parser.xpath('./bpmn:startEvent')
        workflow_end_event = task_parser.xpath('./bpmn:endEvent')
        if len(workflow_start_event) != 1:
            raise ValidationException(
                'Multiple Start points are not allowed in SubWorkflow Task',
                node=task_parser.node,
                filename=task_parser.filename)
        if len(workflow_end_event) == 0:
            raise ValidationException(
                'A SubWorkflow Must contain an End event',
                node=task_parser.node,
                filename=task_parser.filename)

        nsmap = DEFAULT_NSMAP.copy()
        nsmap['camunda'] = "http://camunda.org/schema/1.0/bpmn"
        nsmap['di'] = "http://www.omg.org/spec/DD/20100524/DI"

        # Create wrapper xml for the subworkflow
        for ns, val in nsmap.items():
            etree.register_namespace(ns, val)

        task_parser.process_parser.parser.create_parser(
            task_parser.node,
            filename=task_parser.filename,
            lane=task_parser.lane
        )
        return task_parser.node.get('id')

    @staticmethod
    def get_call_activity_spec(task_parser):
        called_element = task_parser.node.get('calledElement', None)
        if not called_element:
            raise ValidationException(
                'No "calledElement" attribute for Call Activity.',
                node=task_parser.node,
                filename=task_parser.filename)
        parser = task_parser.process_parser.parser.get_process_parser(called_element)
        if parser is None:
            raise ValidationException(
                f"The process '{called_element}' was not found. Did you mean one of the following: "
                f"{', '.join(task_parser.process_parser.parser.get_process_ids())}?",
                node=task_parser.node,
                filename=task_parser.filename)
        return called_element


class CamundaCallActivityParser(SpiffTaskParser):
    """Parses a CallActivity node."""

    def parse_extensions(self, node=None):
        if node is None:
            node = self.node
        return CamundaCallActivityParser._parse_extensions(node)

    @classmethod
    def _node_children_by_tag_name(cls, node, tag_name):
        xpath = cls._camunda_ready_xpath_for_node(node)
        return xpath(f'.//{CAMUNDA_MODEL_PREFIX}:{tag_name}')

    @staticmethod
    def _camunda_ready_xpath_for_node(node):
        extra_ns = {CAMUNDA_MODEL_PREFIX: CAMUNDA_MODEL_NS}
        return xpath_eval(node, extra_ns)

    @staticmethod
    def _parse_extensions(node):
        # Too bad doing this works in such a stupid way.
        # We should set a namespace and automatically do this.
        extensions = SpiffTaskParser._parse_extensions(node)
        extra_ns = {CAMUNDA_MODEL_PREFIX: CAMUNDA_MODEL_NS}
        xpath = xpath_eval(node, extra_ns)
        extension_nodes = xpath(f'./bpmn:extensionElements/{CAMUNDA_MODEL_PREFIX}:*')
        for node in extension_nodes:
            name = etree.QName(node).localname
            if name == 'in':
                if not extensions.get('inputs'):
                    extensions['inputs'] = []
                extensions['inputs'].append(CamundaCallActivityParser._parse_inputs_outputs(node))
            elif name == "out":
                if not extensions.get('outputs'):
                    extensions['outputs'] = []
                extensions['outputs'].append(CamundaCallActivityParser._parse_inputs_outputs(node))
            elif name == "executionListener":
                if node.attrib.get('event') == "start":
                    extensions['pre_script'] = CamundaCallActivityParser._parse_execution_listener(node)
                if node.attrib.get('event') == "end":
                    extensions['post_script'] = CamundaCallActivityParser._parse_execution_listener(node)

        return extensions

    @staticmethod
    def _parse_inputs_outputs(node):
        if node.attrib.get('variables'):
            return {"all": None}
        if node.attrib.get('source'):
            return {node.attrib['source']: node.attrib['target']}

        return {}

    @staticmethod
    def _parse_execution_listener(node):
        script_node = CamundaCallActivityParser._node_children_by_tag_name(node, "script")[0]
        return script_node.text

    def create_task(self):
        extensions = self.parse_extensions()
        subworkflow_spec = CallActivitySubprocessParser.get_call_activity_spec(self)
        return self.spec_class(
            self.spec,
            self.get_task_spec_name(),
            subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None),
            prescript=extensions.get('pre_script'),
            postscript=extensions.get('post_script'))


class CallActivitySubWorkflowParser(SpiffTaskParser):

    def create_task(self):
        extensions = self.parse_extensions()
        inputs = extensions.get('inputs')
        outputs = extensions.get('outputs')

        subworkflow_spec = CamundaCallActivityParser.get_subprocess_spec(self)
        return self.spec_class(
            self.spec, self.get_task_spec_name(), subworkflow_spec,
            lane=self.lane, position=self.position,
            description=self.node.get('name', None),
            inputs=inputs,
            outputs=outputs)
