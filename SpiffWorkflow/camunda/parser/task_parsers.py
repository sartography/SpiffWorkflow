from lxml import etree
from copy import deepcopy

from ...camunda.specs.UserTask import Form, FormField, EnumFormField
from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser
from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.dmn.specs.BusinessRuleTask import BusinessRuleTask
from SpiffWorkflow.task import TaskState
from SpiffWorkflow.spiff.parser.task_spec import SpiffTaskParser
from SpiffWorkflow.bpmn.parser.util import xpath_eval
from SpiffWorkflow.bpmn.parser.ValidationException import ValidationException
from SpiffWorkflow.bpmn.parser.node_parser import DEFAULT_NSMAP
from SpiffWorkflow.bpmn.parser.task_parsers import ScriptTaskParser


CAMUNDA_MODEL_PREFIX = 'camunda'
CAMUNDA_MODEL_NS = 'http://camunda.org/schema/1.0/bpmn'


class BusinessRuleTaskParser(TaskParser):
    dmn_debug = None

    def __init__(self, process_parser, spec_class, node, lane=None):
        nsmap = DEFAULT_NSMAP.copy()
        nsmap.update({'camunda': CAMUNDA_MODEL_NS})
        super(BusinessRuleTaskParser, self).__init__(process_parser, spec_class, node, nsmap, lane)

    def create_task(self):
        decision_ref = self.get_decision_ref(self.node)
        return BusinessRuleTask(self.spec, self.get_task_spec_name(),
                                dmnEngine=self.process_parser.parser.get_engine(decision_ref, self.node),
                                lane=self.lane, position=self.position,
                                description=self.node.get('name', None),
                                )

    @staticmethod
    def get_decision_ref(node):
        return node.attrib['{' + CAMUNDA_MODEL_NS + '}decisionRef']

    def _on_trigger(self, my_task):
        pass

    def serialize(self, serializer, **kwargs):
        pass

    @classmethod
    def deserialize(cls, serializer, wf_spec, s_state, **kwargs):
        pass


class UserTaskParser(TaskParser):
    """
    Base class for parsing User Tasks
    """

    def __init__(self, process_parser, spec_class, node, lane=None):
        nsmap = DEFAULT_NSMAP.copy()
        nsmap.update({'camunda': CAMUNDA_MODEL_NS})
        super(UserTaskParser, self).__init__(process_parser, spec_class, node, nsmap, lane)

    def create_task(self):
        form = self.get_form()
        return self.spec_class(self.spec, self.get_task_spec_name(), form,
                               lane=self.lane,
                               position=self.position,
                               description=self.node.get('name', None))

    def get_form(self):
        """Camunda provides a simple form builder, this will extract the
        details from that form and construct a form model from it. """
        form = Form()
        try:
            form.key = self.node.attrib['{' + CAMUNDA_MODEL_NS + '}formKey']
        except KeyError:
            return form
        for xml_field in self.xpath('.//camunda:formData/camunda:formField'):
            if xml_field.get('type') == 'enum':
                field = self.get_enum_field(xml_field)
            else:
                field = FormField()

            field.id = xml_field.get('id')
            field.type = xml_field.get('type')
            field.label = xml_field.get('label')
            field.default_value = xml_field.get('defaultValue')

            for child in xml_field:
                if child.tag == '{' + CAMUNDA_MODEL_NS + '}properties':
                    for p in child:
                        field.add_property(p.get('id'), p.get('value'))

                if child.tag == '{' + CAMUNDA_MODEL_NS + '}validation':
                    for v in child:
                        field.add_validation(v.get('name'), v.get('config'))

            form.add_field(field)
        return form

    def get_enum_field(self, xml_field):
        field = EnumFormField()

        for child in xml_field:
            if child.tag == '{' + CAMUNDA_MODEL_NS + '}value':
                field.add_option(child.get('id'), child.get('name'))
        return field


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


class CustomScriptTaskParser(ScriptTaskParser):
    """
    Parses a script task
    """
    def create_task(self):
        script = None
        extensions = {}
        try:
            script = self.get_script()
        except Exception:
            script = self.get_resource_script()
            extensions = CamundaCallActivityParser._parse_extensions(self.node)

        if not script:
            raise ValidationException("Invalid Script Task.  No Script Provided. ",
                                      node=self.node, file_name=self.filename)

        return self.spec_class(self.spec, self.get_task_spec_name(), script,
                               lane=self.lane,
                               position=self.position,
                               description=self.node.get('name', None),
                               prescript=extensions.get('pre_script'),
                               postscript=extensions.get('post_script'))

    def get_resource_script(self):
        """
        Gets the script content from the node. A subclass can override this
        method, if the script needs to be pre-parsed. The result of this call
        will be passed to the Script Engine for execution.
        """
        script = None
        try:
            self.node.get("{%s}resource" % CAMUNDA_MODEL_NS)
            method = self.node.get("{%s}resource" % CAMUNDA_MODEL_NS)
            result_var = self.node.get("{%s}resultVariable" % CAMUNDA_MODEL_NS, "_")

            script = """def _temp(task):
                    from %s import %s
                    return %s(task) \n\n""" % (".".join(method.split(".")[:-1]),
                                               method.split(".")[-1], method.split(".")[-1])
            script += "%s = _temp(task)" % result_var

        except AssertionError as ae:
            raise ValidationException("Invalid Script Task.  No Script Provided. " + str(ae),
                                      node=self.node, file_name=self.filename)
        return script
