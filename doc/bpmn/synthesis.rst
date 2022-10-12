Putting it All Together
=======================

In this section we'll be discussing the overall structure of the workflow
runner we developed in `spiff-example-cli <https://github.com/sartography/spiff-example-cli>`_.

Our example application contains two different workflow runners, one that uses tasks with 
Camunda extensions
(`run.py <https://github.com/sartography/spiff-example-cli/blob/main/run.py>`_) and one
that uses tasks with Spiff extensions 
(`run-spiff.py <https://github.com/sartography/spiff-example-cli/blob/main/run.py>`_).

Most of the workflow operations will not change, so shared functions are defined in 
`utils.py <https://github.com/sartography/spiff-example-cli/blob/main/utils.py>`_.

The primary difference is handling user tasks.  Spiff User Tasks define an extensions
property that stores a filename containing a JSON schema used to define a web form.  We
use `react-jsonschema-form <https://react-jsonschema-form.readthedocs.io/en/latest/>`_
to define our forms.  This doesn't necessarily make a lot of sense in terms of a command
line UI, so we'll focus on the Camunda workflow runner in this document.

Loading a Workflow
-------------------

The :code:`CamundaParser` extends the base :code:`BpmnParser`, adding functionality for
parsing forms defined in Camunda User Tasks and decision tables defined in Camunda 
Business Rule Tasks. (There is a similar :code:`SpiffBpmnParser` used by the alternate
runner.)

We create the parser and use it to load our workflow.

.. code:: python

    parser = CamundaParser()
    wf = parse_workflow(parser, args.process, args.bpmn, args.dmn)

Our workflow parser looks like this;

.. code:: python

    def parse_workflow(parser, process, bpmn_files, dmn_files, load_all=True):
        parser.add_bpmn_files(bpmn_files)
        if dmn_files:
            parser.add_dmn_files(dmn_files)
        top_level = parser.get_spec(process)
        if load_all:
            subprocesses = parser.find_all_specs()
        else:
            subprocesses = parser.get_subprocess_specs(process)
        return BpmnWorkflow(top_level, subprocesses, script_engine=CustomScriptEngine)

We'll obtain the workflow specification from the parser for the top level process
using :code:`parser.get_spec()`.

We have two options for finding subprocess specs.  The method :code:`parser.find_all_specs()` 
will create specs for all executable processes found in every file supplied.  The method 
:code:`parser.get_subprocess_specs(process)` will create specs only for processes used by 
the specified process.  Both search recursively for subprocesses; the only difference is 
the latter method limits the search start to the specified process.

Our examples are pretty simple and we're not loading any extraneous stuff, so we'll
just always load everything. If your entire workflow is contained in your top-level
process, you can omit the :code:`subprocess` argument, but if your workflow contains 
call activities, you'll need to use one of these methods to find the models for any 
called processes.

We also provide an enhanced script engine to our workflow.  More information about how and
why you might want to do this is covered in :doc:`advanced`.  The :code:`script_engine`
argument is optional and the default will be used if none is supplied.

We return :code:`BpmnWorkflow` that runs our top-level workflow and contains specs for any 
subprocesses defined by that workflow.

Defining Task Handlers
----------------------

In :code:`run.py`, we define the function :code:`complete_user_task`.  This has code specific
to Camunda User Task specs (in :code:`run-spiff.py`, we do something different).

We also import the shared function :code:`complete_manual_task` for handling Manual
Tasks as there is no difference.

We create a mapping of task type to handler, which we'll pass to our workflow runner.

.. code:: python

    handlers = {
        ManualTask: complete_manual_task,
        UserTask: complete_user_task,
    }

This might not be a step you would need to do in an application you build, since
you would likely have only one set of task specs that need to be parsed, handled, and
serialized; however our `run` method is an awful lot of code to maintain in two separate
files.

Running a Workflow
------------------

This is our application's :code:`run` method.

We pass our workflow, the task handlers, a serializer (creating a serializer is covered in
more depth in :doc:`advanced`).

The :code:`step` argument is a boolean that indicates whether we want the option of seeing
a more detailed representation of the state at each step, which we'll discuss in the
section following this one.  The :code:`display_types` argument controls what types of
tasks should be included in a detailed list when stepping through a process.

.. code:: python

    def run(workflow, task_handlers, serializer, step, display_types):

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
                handler = task_handlers.get(type(next_task.task_spec))
                if handler is not None:
                    handler(next_task)
                next_task.complete()

            workflow.refresh_waiting_tasks()
            workflow.do_engine_steps()
            if step:
                print_state(workflow, next_task, display_types)

        print('\nWorkflow Data')
        print(json.dumps(workflow.data, indent=2, separators=[ ', ', ': ' ]))

The first line of this function is the one that does the bulk of the work in
SpiffWorkflow.  Calling :code:`workflow.do_engine_steps()` causes Spiff to repeatedly
look for and execute any engine tasks that are ready.

An **engine task** does not require user interaction. For instance, it could be
a Script task or selection of a flow from a gateway.  Execution will
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

    def print_state(workflow, task, display_types):

        print('\nLast Task')
        print(format_task(task))
        print(json.dumps(task.data, indent=2, separators=[ ', ', ': ' ]))

        all_tasks = [ task for task in workflow.get_tasks() if isinstance(task.task_spec, display_types) ]
        upcoming_tasks = [ task for task in all_tasks if task.state in [TaskState.READY, TaskState.WAITING] ]

        print('\nUpcoming Tasks')
        for idx, task in enumerate(upcoming_tasks):
            print(format_task(task))

        if input('\nShow all tasks? ').lower() == 'y':
            for idx, task in enumerate(all_tasks):
                print(format_task(task))

We'll print information about our task as described above, as well as a dump of its data.

We can get a list of all tasks regardless of type or state with :code:`workflow.get_tasks()`.

The actual list of tasks will get quite long (some tasks are expanded internally by Spiff into
multiple tasks, and all gateways and events are also treated as "tasks").  So we're filtering
the tasks to only display the ones that would have salience to a user here.

We'll further filter those tasks for :code:`READY` and :code:`WAITING` tasks for a more
compact display, and only show all tasks when explicitly called for.
