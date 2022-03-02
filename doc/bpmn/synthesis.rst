Putting it All Together
=======================

In this section we'll be discussing the overall structure of the workflow
runner we developed in `SpiffExample <https://github.com/sartography/SpiffExample>`_.

Loading a Workflow
-------------------

We'll need the following imports:

.. code:: python

    from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
    from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
    from SpiffWorkflow.dmn.parser.BpmnDmnParser import BpmnDmnParser

We need to create a parser.  We could have imported :code:`BpmnParser`, which
these parsers inherit from, but we need some additional features that the base
parser does not provide.

.. code:: python

    class Parser(BpmnDmnParser):
        OVERRIDE_PARSER_CLASSES = BpmnDmnParser.OVERRIDE_PARSER_CLASSES
        OVERRIDE_PARSER_CLASSES.update(CamundaParser.OVERRIDE_PARSER_CLASSES)

We'll use :code:`BpmnDmnParser` as our base class, because we would like the ability 
to use DMN tables in our application.  The :code:`BpmnDmnParser` provides a task 
parser for Business Rule Tasks, which the underlying :code:`BpmnParser` it inherits from 
does not contain.

We also imported the :code:`CamundaParser` so that we can parse some Camunda
specific features we'll use (forms in User Tasks).  The :code:`CamundaParser` User
Task parser will override the default parser.

In general, any task parser can be replaced with a custom parser of your
own design if you have a BPMN modeller that produces XML not handled by the
BPMN parsers in SpiffWorkflow.

.. code:: python

    def parse(process, bpmn_files, dmn_files):
        parser = Parser()
        parser.add_bpmn_files(bpmn_files)
        if dmn_files:
            parser.add_dmn_files(dmn_files)
        return BpmnWorkflow(parser.get_spec(process), script_engine=CustomScriptEngine)

We create an instance of our previously defined parser, add the BPMN files to it, and
optionally add any DMN files, if they were supplied.

We'll obtain the workflow specification from the parser for the top level process
using :code:`parser.get_spec()` and return a :code:`BpmnWorkflow` based on the spec.

We also provide an enhanced script engine to our workflow.  More information about how and
why you might want to do this is covered in :doc:`advanced`.  The :code:`script_engine`
argument is optional and the default will be used if none is supplied.

Running a Workflow
------------------

This is our application's :code:`run()` method.

The :code:`step` argument is a boolean that indicates whether we want the option of seeing
a more detailed representation of the state at each step, which we'll discuss in the 
section following this one.

.. code:: python

    def run(workflow, step):

        workflow.do_engine_steps()

        while not workflow.is_completed():

            ready_tasks = workflow.get_ready_user_tasks()
            options = { }
            print()
            for idx, task in enumerate(ready_tasks):
                option = format_task(task, False)
                options[str(idx + 1)] = task
                print(f'{idx + 1}. {option}')

            selected = None
            while selected not in options and selected not in ['', 'D', 'd']:
                selected = input('Select task to complete, enter to wait, or D to dump the workflow state: ')

            if selected.lower() == 'd':
                filename = input('Enter filename: ')
                state = BpmnSerializer().serialize_workflow(workflow, include_spec=True)
                with open(filename, 'w') as dump:
                    dump.write(state)
            elif selected != '':
                next_task = options[selected]
                if isinstance(next_task.task_spec, UserTask):
                    complete_user_task(next_task)
                    next_task.complete()
                elif isinstance(next_task.task_spec, ManualTask):
                    complete_manual_task(next_task)
                    next_task.complete()
                else:
                    next_task.complete()

            workflow.refresh_waiting_tasks()
            workflow.do_engine_steps()
            if step:
                print_state(workflow)

        print('\nWorkflow Data')
        print(json.dumps(workflow.data, indent=2, separators=[ ', ', ': ' ]))

The first line of this function is the one that does the bulk of the work in 
SpiffWorkflow.  Calling :code:`workflow.do_engine_steps()` causes Spiff to repeatedly
look for and execute any engine tasks that are ready.

An **engine task** is a task that requires no user interaction (e.g. Business Rule or
Script Tasks) or the evaluation of a gateway and selection of a flow.  Execution will 
stop when only interactive tasks remain or the workflow is completed.

A SpiffWorkflow application will call :code:`workflow.do_engine_steps()` to start the 
workflow and then enter a loop that will

- check for ready user tasks
- present the tasks to the user to complete 
- complete the tasks
- refresh any waiting tasks 
- complete any engine tasks that have been reached via user interactions

until the workflow completes.

When a workflow completes, the task data (just a dictionary passed from one task to the
next, and optionally modified by each task) is copied into the workflow data.  We display 
the end state of the workflow on completion.

The rest of the code is all about presenting the tasks to the user and dumping the
workflow state.  We've covered former in the BPMN Elements section of :doc:`index`
and will cover the latter in :doc:`advanced`.  

Handling task presentation is what **you** will be developing when you use SpiffWorkflow.

Examining the Workflow State
----------------------------

When this application is run and we want to present steps to the user, we'll need
to be able to examine the workflow and task states and associated data.  We'll cover
the basics of this in this section.

The code below is a simple method for displaying information about a task.  We use
this in two ways 

- presenting a list of tasks to a user (in this case the state will always be ready, so we won't include it) 
- presenting the state of each task while stepping through the workflow (in this case you most likely do want to know the state).

.. code:: python

    def format_task(task, include_state=True):
        if hasattr(task.task_spec, 'lane') and task.task_spec.lane is not None:
            lane = f'[{task.task_spec.lane}]' 
        else:
            lane = ''
        state = f'[{task.get_state_name()}]' if include_state else ''
        return f'{lane} {task.task_spec.description} ({task.task_spec.name}) {state}'

We previously went over obtaining the lane information in :doc:`organization`.

We can call :code:`task.get_state_name()` to get a human-readable representation of
a task's state.

We store the value provided in the :code:`name` attribute of the task (the text
entered in the 'Name' field in our sample models) in :code:`task.task_spec.description`.

Here is the code we use for examining the workflow state.

.. code:: python

    def print_state(workflow):

        task = workflow.last_task
        print('\nLast Task')
        print(format_task(task))
        print(json.dumps(task.data, indent=2, separators=[ ', ', ': ' ]))

        display_types = (UserTask, ManualTask, ScriptTask, ThrowingEvent, CatchingEvent)
        all_tasks = [ task for task in workflow.get_tasks() if isinstance(task.task_spec, display_types) ]
        upcoming_tasks = [ task for task in all_tasks if task.state in [Task.READY, Task.WAITING] ]

        print('\nUpcoming Tasks')
        for idx, task in enumerate(upcoming_tasks):
            print(format_task(task))

        if input('\nShow all tasks? ').lower() == 'y':
            for idx, task in enumerate(all_tasks):
                print(format_task(task))

We can find out what the last task was with :code:`workflow.last_task`.  We'll print 
its information as described above, as well as a dump of its data.

We can get a list of all tasks regardless of type or state with :code:`workflow.get_tasks()`.

The actual list of tasks will get quite long (some tasks are expanded internally by Spiff into
multiple tasks, and all gateways and events are also treated as "tasks").  So we're filtering 
the tasks to only display the ones that would have salience to a user here.

We'll further filter those tasks for :code:`READY` and :code:`WAITING` tasks for a more
compact display, and only show all tasks when explicitly called for.

This is a very simple application, so our interactions with tasks are very basic.  You will 
definitely want to see the 'Navigation List' section of :doc:`advanced` for more sophisticated
ways of managing workflow state.

