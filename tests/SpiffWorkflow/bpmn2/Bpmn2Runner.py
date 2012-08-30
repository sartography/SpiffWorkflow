from SpiffWorkflow.Task import Task
from SpiffWorkflow.bpmn2.BpmnWorkflow import BpmnWorkflow
from SpiffWorkflow.bpmn2.Bpmn2Loader import Parser
from SpiffWorkflow.bpmn2.specs.UserTask import UserTask
from tests.SpiffWorkflow.bpmn2.ConsoleMenu import Console_App_Menu

__author__ = 'matth'


def main():

    p = Parser()
    p.add_bpmn_files_by_glob('/home/matth/work/git/customers-git/moc/bpmn/MOC/*.bpmn20.xml')
    spec = p.get_spec('MOC')

    workflow = BpmnWorkflow(spec)

    exit_flag = None
    while not exit_flag:

        auto_tasks = filter(lambda t: not isinstance(t.task_spec, UserTask), workflow.get_tasks(Task.READY))
        while auto_tasks:
            for task in auto_tasks:
                task.complete()
            auto_tasks = filter(lambda t: not isinstance(t.task_spec, UserTask), workflow.get_tasks(Task.READY))

        user_tasks = filter(lambda t: isinstance(t.task_spec, UserTask), workflow.get_tasks(Task.READY))

        if not user_tasks:
            exit_flag = True
        else:

            options = ['Exit', 'View Workflow State']
            option_lookup = {}

            for task in user_tasks:
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
            elif selected[2] == 'View Workflow State':
                workflow.dump()
            else:
                (task, choice) = option_lookup[selected[0]]
                task.task_spec.do_choice(task, choice)




if __name__ == '__main__':
    main()