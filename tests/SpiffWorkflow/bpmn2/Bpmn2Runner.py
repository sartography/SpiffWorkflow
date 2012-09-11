import sys
from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn2.BpmnWorkflow import BpmnWorkflow
from SpiffWorkflow.bpmn2.specs.UserTask import UserTask
from tests.SpiffWorkflow.bpmn2.Bpmn2LoaderForTests import TestBpmnParser
from tests.SpiffWorkflow.bpmn2.ConsoleMenu import Console_App_Menu

__author__ = 'matth'

def main():
    workflow_files = sys.argv[1]
    workflow_name = sys.argv[2]

    p = TestBpmnParser()
    p.add_bpmn_files_by_glob(workflow_files)
    spec = p.get_spec(workflow_name)

    workflow = BpmnWorkflow(spec)

    exit_flag = None
    while not exit_flag:

        workflow.refresh_waiting_tasks()
        workflow.do_engine_steps()

        if workflow.is_completed():
            exit_flag = True
        else:

            options = ['Exit', 'View Spec', 'View Workflow State']
            option_lookup = {}

            for task in workflow.get_ready_user_tasks():
                for choice in task.task_spec.get_user_choices():
                    choice_description = '%s - %s [%s]' % (task.task_spec.lane, choice or 'OK', task.task_spec.description)
                    options.append(choice_description)
                    option_lookup[len(options)-1] = (task, choice)


            menu = Console_App_Menu(title='Console BPMN2 Runner')
            menu.set_options('low', tuple(options))
            menu.log('Welcome, please select an option to continue...')
            selected = menu.option()
            if selected[2] == 'Exit':
                exit_flag = True
            elif selected[2] == 'View Spec':
                workflow.spec.dump()
            elif selected[2] == 'View Workflow State':
                workflow.dump()
            else:
                (task, choice) = option_lookup[selected[0]]
                task.task_spec.do_choice(task, choice)


if __name__ == '__main__':
    main()