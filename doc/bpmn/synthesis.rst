Putting it All Together
=======================

In this section we'll be discussing the overall structure of the workflow
runner we developed in `spiff-example-cli <https://github.com/sartography/spiff-example-cli>`_.

Our example application contains two different workflow runners, one that uses tasks with with Spiff extensions
(`spiff-bpmn-runner.py <https://github.com/sartography/spiff-example-cli/blob/main/spiff-bpmn-runner.py>`_) 
and one that uses tasks Camunda extensions
(`camunda-bpmn-runner.py <https://github.com/sartography/spiff-example-cli/blob/main/camunda-bpmn-runner.py>`_).

The primary differences between the two are in handling User and MultiInstance Tasks.  We have some documentation
about how we interpret Camunda forms in :doc:`camunda/tasks`.  That particular page comes from an earlier version of
our documentation, and `camunda-bpmn-runner.py` can run workflows with these tasks.  However, we are not actively
maintaining the :code:`camunda` package any longer.

Base Application Runner
-----------------------

The core functions your application will have to accomodate are

* parsing workflows
* serializing workflows
* running workflows

Task specs define how tasks are executed, and creating the task specs depends on a parser which initializes a spec of 
the appropriate class.  And of course serialization is also heavily dependent on the same information needed to create
the instance.  To that end, our BPMN runner requires that you provide a parser and serializer; it can't operate unless
it knows what to do with each task spec it runs across.

Here is the initialization for the :code:`runner.SimpleBpmnRunner` class that is used by both scripts.

.. code:: python

    def __init__(self, parser, serializer, script_engine=None, handlers=None):

        self.parser = parser
        self.serializer = serializer
        self.script_engine = script_engine
        self.handlers = handlers or {}
        self.workflow = None

If you read the introduction to BPMN, you'll remember that there's a Script Task; the script engine executes scripts
against the task data and updates it.  Gateway conditions are also evaluated against the same context by the engine.

SpiffWorkflow provides a default scripting environment that is suitable for simple applications, but a serious application
will probably need to extend (or restrict) it in some way.  See :doc:`advanced` for a few examples.  Therefore, we have the
ability to optionally pass one in.

The `handlers` argument allows us to let our application know what to do with specific task spec types.  It's a mapping
of task spec class to its handler.  Most task specs won't need handlers outside of how SpiffWorkflow executes them 
(that's probably why you are using this library).  You'll only have to be concerned with the task spec types that
require human interaction; Spiff will not handle those for you.  In your application, these will probably be built into
it and you won't need to pass anything in.

However, here we're trying to build something flexible enough that it can at least deal with two completely different
mechanisms for handling User Tasks, and provide a means for you to experiment with this application.


Parsing Workflows
-----------------

Here is the method we use to parse the workflows;

.. code:: python

    def parse(self, name, bpmn_files, dmn_files=None, collaboration=False):

        self.parser.add_bpmn_files(bpmn_files)
        if dmn_files:
            self.parser.add_dmn_files(dmn_files)

        if collaboration:
            top_level, subprocesses = self.parser.get_collaboration(name)
        else:
            top_level = self.parser.get_spec(name)
            subprocesses = self.parser.get_subprocess_specs(name)
        self.workflow = BpmnWorkflow(top_level, subprocesses, script_engine=self.script_engine)

We add the BPMN and DMN files to the parser and use :code:`parser.get_spec` to create a workflow spec for a process
model.

SpiffWorkflow needs at least one spec to create a workflow; this will be created from the name of the process passed
into the method.  It also needs specs for any subprocesses or call activities.  The method
:code:`parser.get_subprocess_specs` will search recursively through a starting spec and collect specs for all 
referenced resources.

It is possible to have two processes defined in a single model, via a Collaboration.  In this case, there is no "top 
level spec".  We can use :code:`self.parser.get_collaboration` to handle this case.

.. note::

    The only required argument to :code:`BpmnWorkflow` is a single workflow spec, in this case `top_level`.  The
    parser returns an empty dict if no subprocesses are present, but it is not required to pass this in.  If there 
    are subprocess present, `subprocess_specs` will be a mapping of process ID to :code:`BpmnWorkflowSpec`.

In :code:`simple_bpmn_runner.py` we create the parser like this:

.. code:: python

    from SpiffWorkflow.spiff.parser.process import SpiffBpmnParser, BpmnValidator
    parser = SpiffBpmnParser(validator=BpmnValidator())

The validator is an optional argument, which can be used to validate the BPMN files passed in.  The :code:`BpmnValidator`
in the :code:`spiff` package is configured to validate against the BPMN 2.0 spec and our spec describing our own
extensions.

The parser we imported is pre-configured to create task specs that know about Spiff extensions.

There are parsers in both the :code:`bpmn` and :code:`camunda` packages that can be similarly imported.  There is a
validator that uses only the BPMN 2.0 spec in the :code:`bpmn` package (but no similar validator for Camunda).

It is possible to override particular task specs for specific BPMN Task types.  We'll cover an example of this in
:doc:`advanced`.

Serializing Workflows
---------------------

In addition to the pre-configured parser, each package has a pre-configured serializer.

.. code:: python

    from SpiffWorkflow.spiff.serializer.config import SPIFF_SPEC_CONFIG
    from runner.product_info import registry
    wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(SPIFF_SPEC_CONFIG)
    serializer = BpmnWorkflowSerializer(wf_spec_converter, registry)

The serializer has two components:

* the `workflow_spec_converter`, which knows about objects inside SpiffWorkflow
* the `registry`, which can tell SpiffWorkflow how to handle arbitrary data from your scripting environment
  (required only if you have non-JSON-serializable data there).

We discuss the creation and use of `registry` in :doc:`advanced` so we'll ignore it for now.

`SPIFF_SPEC_CONFIG` has serialization methods for each of the task specs in its parser and we can create a
converter from it directly and pass it into our serializer.

Here is our deserialization code:

.. code:: python

    def restore(self, filename):
        with open(filename) as fh:
            self.workflow = self.serializer.deserialize_json(fh.read())
            if self.script_engine is not None:
                self.workflow.script_engine = self.script_engine

We'll just pass the contents of the file to the serializer and it will restore the workflow. The scripting environment
was not serialized, so we have to make sure we reset it.

And here is our serialization code:

.. code:: python

    def dump(self):
        filename = input('Enter filename: ')
        with open(filename, 'w') as fh:
            dct = self.serializer.workflow_to_dict(self.workflow)
            dct[self.serializer.VERSION_KEY] = self.serializer.VERSION
            fh.write(json.dumps(dct, indent=2, separators=[', ', ': ']))

The serializer has a companion method :code:`serialize_json` but we're bypassing that here so that we can make the
output readable.

The heart of the serialization process actually happens in :code:`workflow_to_dict`.  This method returns a
dictionary representation of the workflow that contains only JSON-serializable items.  All :code:`serialize_json` 
does is add a serializer version and call :code:`json.dumps` on the returned dict.  If you are developing a serious
application, it is unlikely you want to store the entire workflow as a string, so you should be aware that this method
exists.

The serializer is fairly complex: not only does it need to handle SpiffWorkflow's own internal objects that it
knows about, it needs to handle arbitrary Python objects in the scripting environment.  The serializer is covered in
more depth in :doc:`advanced`.

Defining Task Handlers
----------------------

In :code:`spiff-bpmn-runner.py`, we also define the functions :code:`complete_user_task`. and
:code:`complete_manual_task`.

We went over these handlers in :doc:`tasks`, so we won't delve into them here.

We create a mapping of task type to handler, which we'll pass to our workflow runner.

.. code:: python

    handlers = {
        UserTask: complete_user_task,
        ManualTask: complete_manual_task,
        NoneTask: complete_manual_task,
    }

In SpiffWorkflow the :code:`NoneTask` (which corresponds to the `bpmn:task` is treated as a human task, and therefore
has no built in way of handling them.  Here we treat them as if they were Manual Tasks.

Running Workflows
-----------------

Our application's :code:`run_workflow` method takes one argument: `step` is a boolean that lets the runner know
if if should stop and present the menu at every step (if :code:`True`) or only where there are human tasks to
complete.

.. code:: python

    def run_workflow(self, step=False):

        while not self.workflow.is_completed():

            if not step:
                self.advance()

            tasks = self.workflow.get_tasks(TaskState.READY|TaskState.WAITING)
            runnable = [t for t in tasks if t.state == TaskState.READY]
            human_tasks = [t for t in runnable if t.task_spec.manual]
            current_tasks = human_tasks if not step else runnable

            self.list_tasks(tasks, 'Ready and Waiting Tasks')
            if len(current_tasks) > 0:
                action = self.show_workflow_options(current_tasks)
            else:
                action = None
                if len(tasks) > 0:
                    input("\nPress any key to update task list")

In the code above we first get the list of all `READY` or `WAITING` tasks; these are the currently active tasks.
`READY` tasks can be run, and `WAITING` tasks may change to `READY` (see :doc:`../concepts` for a discussion of task 
states).  We aren't going to do anything with the `WAITING` tasks except display them.

We can further filter our runnable tasks on the :code:`task_spec.manual` attribute.  If we're stepping though the
workflow, we'll present the entire list; otherwise only the human tasks.  There are actually many points where no
human tasks are available to execute; the :code:`advance` method runs the other runnable tasks if we've opted to
skip displaying them; we'll look at that method after this one.

There may also be points where there are no runnable tasks at all (for example, if the entire process is waiting
on a timer).  In that case, we'll do nothing until the user indicates we can proceeed (the timer will fire
regardless of what the user does -- we're just preventing this loop from executing repeatedly when there's nothing
to do).

.. code:: python

            if action == 'r':
                task = self.select_task(current_tasks)
                handler = self.handlers.get(type(task.task_spec))
                if handler is not None:
                    handler(task)
                task.run()

In the code above, we present a menu of runnable tasks to the user and run the one they chose, optionally
calling one of our handlers.

Each task has a `data` attribute, which can by optionally updated when the task is `READY` and before it is
run.  The task `data` is just a dictionary.  Our handler modifies the task data if necessary (eg adding data
collected from forms), and :code:`task.run` propogates the data to any tasks following it, and changes its state to
one of the `FINISHED` states; nothing more will be done with this task after this point.

We'll skip over most of the options in :code:`run_workflow` since they are pretty straightforward.

.. code:: python

    self.workflow.refresh_waiting_tasks()

At the end of each iteeration, we call :code:`refresh_waiting_tasks` to ensure that any currently `WAITING` tasks
will move to `READY` if they are able to do so.

After the workflow finishes, we'll give the user a few options for looking at the end state.

.. code:: python

        while action != 'q':
            action = self.show_prompt('\nSelect action: ', {
                'a': 'List all tasks',
                'v': 'View workflow data',
                'q': 'Quit',
            }) 
            if action == 'a':
            self.list_tasks([t for t in self.workflow.get_tasks() if t.task_spec.bpmn_id is not None], "All Tasks")
            elif action == 'v':
                dct = self.serializer.data_converter.convert(self.workflow.data)
                print('\n' + json.dumps(dct, indent=2, separators=[', ', ': ']))

Note that we're filtering the task lists with :code:`t.task_spec.bpmn_id is not None`.  The workflow contains
tasks other than the ones visible on the BPMN diagram; these are tasks that SpiffWorkflow uses to manage execution
and we'll omit them from the displays.  If a task is visible on a diagram it will have a non-null value for its
`bpmn_id` attribute (because all BPMN elements require IDs), otherwise the value will be :code:`None`.  See
:doc:`advanced` for more information about BPMN task spec attributes.

When a workflow completes, the task data from the "End" task, which has built up through the operation of the
workflow, is copied into the workflow data, so we want to give the option to display this end state.  We're using
the serializer's `data_converter` to handle the workflow data (the `registry`) we passed in earlier, because
it may arbitrary data.

Let's take a brief look at the advance method:

.. code:: python

    def advance(self):
        engine_tasks = [t for t in self.workflow.get_tasks(TaskState.READY) if not t.task_spec.manual]
        while len(engine_tasks) > 0:
            for task in engine_tasks:
                task.run()
            self.workflow.refresh_waiting_tasks()
            engine_tasks = [t for t in self.workflow.get_tasks(TaskState.READY) if not t.task_spec.manual]

This method is really just a condensed version of :code:`run_workflow` that ignore human tasks and doesn't need to
present a menu.  We use it to get to a point in our workflow where there are only human tasks left to run.

In general, an application that uses SpiffWorkflow will use these methods as a template.  It will consist of a
loop that: 

* runs any `READY` engine tasks (where :code:`task_spec.manual == False`)
* presents `READY` human tasks to users (if any)
* updates the human task data if necessary
* runs the human tasks
* refreshes any `WAITING` tasks

until there are no tasks left to complete.

The rest of the code is all about presenting the tasks to the user and dumping the workflow state.  These are the
parts that you'll want to customize in your own application.

