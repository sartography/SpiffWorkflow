from .sub_process_task import CamundaSubWorkflowTask


class CamundaCallActivity(CamundaSubWorkflowTask):
    def __init__(self, wf_spec, name, subworkflow_spec, **kwargs):
        super(CamundaCallActivity, self).__init__(wf_spec, name, subworkflow_spec, False, **kwargs)
