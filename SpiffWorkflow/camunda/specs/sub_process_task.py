from SpiffWorkflow.bpmn.specs.SubWorkflowTask import SubWorkflowTask


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
