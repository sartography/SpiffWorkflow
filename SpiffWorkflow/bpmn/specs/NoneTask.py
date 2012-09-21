from SpiffWorkflow.bpmn.specs.UserTask import UserTask

__author__ = 'matth'

class NoneTask(UserTask):
    """
    Task Spec for a bpmn:task node. In the base framework, it is assumed that a task with an unspecified type
    is actually a user task
    """
    pass