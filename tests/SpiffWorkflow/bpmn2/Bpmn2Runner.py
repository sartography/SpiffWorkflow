from SpiffWorkflow.Task import Task
from SpiffWorkflow.Workflow import Workflow
from SpiffWorkflow.bpmn2.Bpmn2Loader import Parser
from SpiffWorkflow.bpmn2.specs.UserTask import UserTask
from tests.SpiffWorkflow.bpmn2.ConsoleMenu import Console_App_Menu

__author__ = 'matth'


def main():

    #f = open('/home/matth/Desktop/MOC.bpmn', 'r')
    f = open('/home/matth/Desktop/stage_1_bonita.bpmn', 'r')
    with(f):
        p = Parser(f)
        p.parse()

    workflow = Workflow(p.spec)

    exit_flag = None
    while not exit_flag:

        auto_tasks = filter(lambda t: not isinstance(t.task_spec, UserTask), workflow.get_tasks(Task.READY))
        while auto_tasks:
            for task in auto_tasks:
                workflow.complete_task_from_id(task.id)
            auto_tasks = filter(lambda t: not isinstance(t.task_spec, UserTask), workflow.get_tasks(Task.READY))

        user_tasks = filter(lambda t: isinstance(t.task_spec, UserTask), workflow.get_tasks(Task.READY))

        if not user_tasks:
            exit_flag = True
        else:

            options = ['Exit']
            option_lookup = {}

            for task in user_tasks:
                for choice in task.task_spec.get_user_choices():
                    choice_description = '%s [%s]' % (choice, task.task_spec.description)
                    options.append(choice_description)
                    option_lookup[len(options)-1] = (task, choice)


            menu = Console_App_Menu(title='Console BPMN2 Runner')
            menu.set_options('low', tuple(options))
            menu.log('Welcome, please select an option to continue...')
            selected = menu.option()
            if selected[2] == 'Exit':
                exit_flag = True
            else:
                (task, choice) = option_lookup[selected[0]]
                task.set_attribute(choice=choice)
                workflow.complete_task_from_id(task.id)




if __name__ == '__main__':
    main()