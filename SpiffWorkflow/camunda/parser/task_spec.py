from copy import deepcopy

from ...camunda.specs.UserTask import Form, FormField, EnumFormField

from SpiffWorkflow.bpmn.parser.TaskParser import TaskParser
from SpiffWorkflow.bpmn.parser.node_parser import DEFAULT_NSMAP
from SpiffWorkflow.bpmn.specs.BpmnSpecMixin import BpmnSpecMixin
from SpiffWorkflow.bpmn.specs.SubWorkflowTask import SubWorkflowTask
from SpiffWorkflow.dmn.specs.BusinessRuleTask import BusinessRuleTask
from SpiffWorkflow.task import TaskState

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


class CamundaSubWorkflowTask(SubWorkflowTask):

    def __init__(self, wf_spec, name, subworkflow_spec, transaction=False, **kwargs):
        """
        Constructor.
        :param bpmn_wf_spec: the BpmnProcessSpec for the sub process.
        :param bpmn_wf_class: the BpmnWorkflow class to instantiate
        """
        super(CamundaSubWorkflowTask, self).__init__(wf_spec, name, subworkflow_spec, transaction, **kwargs)
        self.call_activity_pre_data = {}

    def _on_subworkflow_completed(self, subworkflow, my_task):
        # Shouldn't this always be true?
        if isinstance(my_task.parent.task_spec, BpmnSpecMixin):
            my_task.parent.task_spec._child_complete_hook(my_task)

        extensions = {}
        outputs = {}
        is_all_outputs = False
        if hasattr(my_task.task_spec, 'extensions'):
            extensions = my_task.task_spec.extensions

        for wf_input in extensions.get("outputs", []):
            source = list(wf_input.keys())[0]
            target = wf_input[source]

            if source == "all" and not target:
                is_all_outputs = True
                continue
            else:
                s = subworkflow.last_task.get_data(source)
                if not s:
                    raise Exception("Source variable `%s` is not found in data." % source)
                source = s

            outputs[target] = source

        my_task.data = self.call_activity_pre_data
        if is_all_outputs:
            # Copy all task data into start task if no inputs specified
            my_task.set_data(**subworkflow.last_task.data)

        my_task.set_data(**outputs)
        my_task._set_state(TaskState.READY)

    def start_workflow(self, my_task):
        subworkflow = my_task.workflow.get_subprocess(my_task)
        start = subworkflow.get_tasks_from_spec_name('Start', workflow=subworkflow)

        self.call_activity_pre_data = deepcopy(my_task.data)
        extensions = {}
        inputs = {}
        is_all_inputs = False
        if hasattr(my_task.task_spec, 'extensions'):
            extensions = my_task.task_spec.extensions

        for wf_input in extensions.get("inputs", []):
            source = list(wf_input.keys())[0]
            target = wf_input[source]

            if source == "all" and not target:
                is_all_inputs = True
                continue
            elif '"' in source:
                source = str(source.replace('"', ""))
            else:
                s = my_task.get_data(source)
                if not s:
                    raise Exception("Source variable `%s` is not found in data." % source)
                source = s

            inputs[target] = source

        if is_all_inputs:
            # Copy all task data into start task if no inputs specified
            start[0].set_data(**my_task.data)

        start[0].set_data(**inputs)

        for child in subworkflow.task_tree.children:
            child.task_spec._update(child)

        my_task._set_state(TaskState.WAITING)


class CamundaCallActivity(CamundaSubWorkflowTask, TaskParser):
    def __init__(self, wf_spec, name, subworkflow_spec, **kwargs):
        super(CamundaCallActivity, self).__init__(wf_spec, name, subworkflow_spec, False, **kwargs)
