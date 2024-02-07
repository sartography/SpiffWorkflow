Instantiating a Workflow
========================

From the :code:`start_workflow` method of our BPMN engine (:app:`engine/engine.py`):

.. code-block:: python

    def start_workflow(self, spec_id):
        spec, sp_specs = self.serializer.get_workflow_spec(spec_id)
        wf = BpmnWorkflow(spec, sp_specs, script_engine=self._script_engine)
        wf_id = self.serializer.create_workflow(wf, spec_id)
        return wf_id

We'll use our serializer to recreate the workflow spec based on the id.  As discussed in :ref:`parsing_subprocesses`,
a process has a top level specification and dictionary of process id -> spec containing any other processes referenced
by the top level process (Call Actitivies and Subprocesses).

Running a Workflow
==================

In the simplest case, running a workflow involves implementing the following loop:

* runs any `READY` engine tasks (where :code:`task_spec.manual == False`)
* presents `READY` human tasks to users (if any)
* updates the human task data if necessary
* runs the human tasks
* refreshes any `WAITING` tasks

until there are no tasks left to complete.

Here are our engine methods:

.. code-block:: python

    def run_until_user_input_required(self, workflow):
        task = workflow.get_next_task(state=TaskState.READY, manual=False)
        while task is not None:
            task.run()
            self.run_ready_events(workflow)
            task = workflow.get_next_task(state=TaskState.READY, manual=False)

    def run_ready_events(self, workflow):
        workflow.refresh_waiting_tasks()
        task = workflow.get_next_task(state=TaskState.READY, spec_class=CatchingEvent)
        while task is not None:
            task.run()
            task = workflow.get_next_task(state=TaskState.READY, spec_class=CatchingEvent)

In the first, we retrieve and run any tasks that can be executed automatically, including processing any events that
might have occurred.

The second method handles processing events.  A task that corresponds to an event remains in state :code:`WAITING` until
it catches whatever event it is waiting on, at which point it becomes :code:`READY` and can be run.  The
:code:`workflow.refresh_waiting_tasks` method iterates over all the waiting tasks and changes the state to :code:`READY`
if the conditions for doing so have been met.

We'll cover using the `workflow.get_next_task` method and handling Human tasks later in this document.

Tasks
=====

In this section, we'll give an overview of some of the general attributes of Task Specs and then delve into a few
specific types.  See :ref:`specs_vs_instances` to read about Tasks vs Task Specs.

BPMN Task Specs
---------------

BPMN Task Specs inherit quite a few attributes from :code:`SpiffWorkflow.specs.base.TaskSpec`, but you probably
don't have to pay much attention to most of them.  A few of the important ones are:

* `name`: the unique id of the TaskSpec, and it will correspond to the BPMN ID if that is present
* `description`: we use this attribute to provide a description of the BPMN task type
* `manual`: :code:`True` if human input is required to complete tasks associated with this Task Spec

BPMN Task Specs have the following additional attributes.

* `bpmn_id`: the ID of the BPMN Task (this will be :code:`None` if the task is not visible on the diagram)
* `bpmn_name`: the BPMN name of the Task
* `lane`: the lane of the BPMN Task
* `documentation`: the contents of the BPMN `documentation` element for the Task

In the example application, we use these :code:`bpmn_name` (or :code:`name` when a :code:`bpmn_name` isn't specified),
and :code:`lane` to display information about the tasks in a workflow (see the :code:`update_task_tree` method of
:app:`curses_ui/workflow_view.py`).

The :code:`manual` attribute is particularly important, because SpiffWorkflow does not include built-in
handling of these tasks so you'll need to implement this as part of your application.  We'll go over how this is
handled in this application in the next section.

.. note::

    NoneTasks (BPMN tasks with no more specific type assigned) are treated as Manual Tasks by SpiffWorkflow.

Instantiated Tasks
------------------

Actually all Tasks are instantiated -- that is what distinguishes a Task from a Task Spec; however, it is impossible to
belabor this point too much.

Tasks have a few additional attributes that contain important details about particular instances:

* :code:`id`: a UUID that uniquely identifies the Task (remember that a Task Spec may be reached more than once, but a new
  Task is created each time)
* :code:`task_spec`: the Task Spec associated with this Task
* :code:`state`: the state of the Task, represented as one of the values in :code:`TaskState`
* :code:`last_state_change`: the timestamp of the last time this Task changed state
* :code:`data`: a dictionary that holds task/workflow data

Human (User and Manual) Tasks
-----------------------------

Remember that the :code:`bpmn` module does not provide any default capability for gathering information from a user,
and this is something you'll have to implement.  In this example, we'll assume that we are using Task Specs from the
:code:`spiff` module (there is an alternative implementation in the :code:`camunda` module).

Spiff Arena uses JSON schemas to define forms associated with User Tasks and
`react-jsonschema-form <https://github.com/rjsf-team/react-jsonschema-form>`_ to render them.  Additionally, our User
and Manual tasks have a custom extension :code:`instructionsForEndUser` which stores a Jinja template with Markdown
formatting that is rendered using the task data.  A different format for defing forms could be used and Jinja and
Markdown could be easily replaced by other templating and rendering schemes depending on your application's needs.

Our User and Manual Task handlers render the instructions (this code is from :app:`spiff/curses_handlers.py`):

.. code-block:: python

    from jinja2 import Template

    def get_instructions(self):
        instructions = f'{self.task.task_spec.bpmn_name}\n\n'
        text = self.task.task_spec.extensions.get('instructionsForEndUser')
        if text is not None:
            template = Template(text)
            instructions += template.render(self.task.data)
        instructions += '\n\n'
        return instructions

We're not going to attempt to handle Markdown in a curses UI, so we'll assume we just have text.  However, we do
want to be able to incorporate data specific to the workflow in information that is presented to a user; this is
something that your application will certainly need to do.  Here, we use the :code:`data` attribute of the Task
(recall that this is a dictionary) to render the template.

Our application contains a :code:`Field` class (defined in :app:`curses_ui/user_input.py`) that tells us
how to convert to and from a string representation that can be displayed on the screen and can interact with the form
display screen.  Our User Task handler also has a method for translating a couple of basic JSON schema types into
something that can be displayed (supporting only text, integers, and 'oneOf').  The form screen collects and validates
the user input and collects the results in a dictionary.

We won't go into the details about how the form screen works, as it's specific to this application rather than the
library itself; instead we'll skip to the code that runs the task after it has been presented to the user; any
application needs to do this.

Simply running the task is sufficient for Manual Tasks.

.. code-block:: python

    def on_complete(self, results):
        self.task.run()

However, we need to extend this method for User Tasks, to incorporate the user-submitted data into the workflow:

.. code-block:: python

    def on_complete(self, results):
        self.task.set_data(**results)
        super().on_complete(results)

Here we are setting a key for each field in the form.  Other possible options here are to set one key that contains
all of the form data, or map the schema to Python class and use that in lieu of a dictionary.  It's up to you to
decide the best way of managing this.

The key points here are that your application will need to have the capability to display information, potentially
incorporating data from the workflow instance, as well as update this data based on user input.  We'll go through a
simple example next.

We'll refer to the process modeled in :bpmn:`task_types.bpmn` contains a simple form which asks a user to input a
product and quantity as well a manual task presenting the order information at the end of the process (the form is
defined in :form:`select_product_and_quantity.json`

After the user submits the form, we'll collect the results in the following dictionary:

.. code-block:: python

    {
        'product_name': 'product_a',
        'product_quantity': 2,
    }

We'll add these variables to the task data before we run the task.  The Business Rule task looks up the price from a
DMN table based on :code:`product_name` and the Script Task sets :code:`order_total` based on the price and quantity.

Our Manual Task's instructions look like this:

.. code-block::

    Order Summary
    {{ product_name }}
    Quantity: {{ product_quantity }}
    Order Total: {{ order_total }}

and when rendered against the instance data, reflects the details of this particular order.

Business Rule Tasks
-------------------

Business Rule Tasks are not implemented in the :code:`SpiffWorkflow.bpmn` module; however, the library does contain
a DMN implementation of a Business Rule Task in the :code:`SpiffWorkflow.dmn` module.  Both the :code:`spiff` and
:code:`camunda` modules include DMN support.

Gateways
--------

You will not need special code to handle gateways (this is one of the things this library does for you), but it is
worth emphasizing that gateway conditions are treated as Python expressions which are evaluated against the context of
the task data.  See :doc:`script_engine` for more details.

Script and Service Tasks
------------------------

See :doc:`script_engine` for more information about how Spiff handles these tasks.  There is no default Service Task
implementation, but we'll go over an example of one way this might be implemented there.  Script tasks assume the
:code:`script` attribute contains the text of a Python script, which is executed in the context of the task's data.

.. _task_filters:

Filtering Tasks
===============

SpiffWorkflow has two methods for retrieving tasks:

- :code:`workflow.get_tasks`: returns a list of matching tasks, or an empty list
- :code:`workflow.get_next_task`: returns the first matching task, or None

Both of these methods use the same helper classes and take the same arguments -- the only difference is the return
type.

These methods return a :code:`TaskIterator`, which in turn uses a :code:`TaskFilter` to determine what tasks match.

Tasks can be filtered by:

- :code:`state`: a :code:`TaskState` value (see :ref:`states` for the possible states)
- :code:`spec_name`: the name of a Task Spec (this will typically correspond to the BPMN ID)
- :code:`manual`: whether the Task Spec requires manual input
- :code:`updated_ts`: limits results to after the provided timestamp
- :code:`spec_class`: limits results to a particular Task Spec class
- :code:`lane`: the lane of the Task Spec
- :code:`catches_event`: Task Specs that catch a particular :code:`BpmnEvent`

Examples
--------

We reference the following processes here:

- :bpmn:`top_level.bpmn`
- :bpmn:`call_activity.bpmn`

To filter by state, We need to import the :code:`TaskState` object (unless you want to memorize which numbers
correspond to which states).

.. code-block:: python

    from SpiffWorkflow.util.task import TaskState

Ready Human Tasks
^^^^^^^^^^^^^^^^^

.. code-block:: python

    tasks = workflow.get_tasks(state=TaskState.READY, manual=False)

Completed Tasks
^^^^^^^^^^^^^^^

.. code-block:: python

    tasks = workflow.get_tasks(state=TaskState.COMPLETED)

Tasks by Spec Name
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    tasks = workflow.get_tasks(spec_name='customize_product')

will return a list containing the Call Activities for the customization of a product in our example workflow.

Tasks Updated After
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    ts = datetime.now() - timedelta(hours=1)
    tasks = workflow.get_tasks(state=TaskState.WAITING, updated_ts=ts)

Returns Tasks that changed to :code:`WAITING` in the past hour.

Tasks by Lane
^^^^^^^^^^^^^

.. code:: python

     ready_tasks = workflow.get_tasks(state=TaskState.READY, lane='Customer')

will return only Tasks in the 'Customer' lane in our example workflow.

Subprocesses and Call Activities
================================

In the first section of this document, we noted that :code:`BpmnWorkflow` is instantiated with a top level spec as
well as a collection of specs for any referenced processes.  The instantiated :code:`BpmnSubWorkflows` are maintained
as mapping of :code:`task.id` to :code:`BpmnSubworkflow` in the :code:`subprocesses` attribute.

Both classes inherit from :code:`Workflow` and maintain tasks in separate task trees.  However, only 
:code:`BpmnWorkflow` maintains subworkflow information; even deeply nested workflows are stored at the top level (for
ease of access).

Task iteration also works differently as well. :code:`BpmnWorkflow.get_tasks` has been extended to retrieve
subworkflows associated with tasks and iterate over those as well; when iterating over tasks in a
:code:`BpmnSubWorkflow`, only tasks from that workflow will be returned.

.. code-block:: python

    task = workflow.get_next_task(spec_name='customize_product')
    subprocess = workflow.get_subprocess(task)
    subprocess_tasks = subprocess.get_tasks()

This code block finds the first product customization of our example workflow and gets only the tasks inside that
workflow.

A :code:`BpmnSubworkflow` always uses the top level workflow's script engine, to ensure consistency.

Additionally, the class has a few extra attributes to make it more convenient to navigate across nested workflows:

- :code:`subworkflow.top_workflow` returns the top level workflow
- :code:`subworkflow.parent_task_id` returns the UUID of the task the workflow is associated with
- :code:`parent_workflow`: returns the workflow immediately above it in the stack

These methods exist on the top level workflow as well, and return :code:`None`.

Events
======

BPMN Events are represented by :code:`BpmnEvent` class.  An instance of this class contains an :code:`EventDefinition`,
an optional payload, message correlations for Messages that define them, and (also optionally) a target subworkflow.
The last property is used internally by SpiffWorkflow by subworkflows that need to communicate with other subworkflows
and can be safely ignored.

The relationship between the :code:`EventDefinition` and :code:`BpmnEvent` is analagous to that of :code:`TaskSpec`
and :code:`Task`: a :code:`TaskSpec` defining a BPMN Event has an additional :code:`event_definition` attribute that
contains the information about the Event that will be caught or thrown.

When an event is thrown, a :code:`BpmnEvent` will be created using the :code:`EventDefinition` associated with the
task's spec, and payload, if applicable.  For events with payloads, the :code:`EventDefinition` will define how to
create the payload based on the workflow instance and include this with the event.  A Timer Event will know how to
parse and evaluate the provided expression.  And so forth.

The event will be passed to the :code:`workflow.catch` method, which will iterate over the all the tasks and pass the
event to any tasks that are waiting for that event.  If no tasks that catch the event are present in the workflow, the
event will placed in a pending event queue and these events can be retrieved with the :code:`workflow.get_events`
method.

.. note::

    This method clears the event queue, so if your application retrieves the event and does not handle it, it is gone
    forever!

The application in this repo is designed to run single workflows, so it does not have any external event handling.
If you implement such functionality, you'll need a way of identifying which processes any retrieved events should be
sent to.

The :code:`workflow.waiting_events` will return a list of :code:`PendingBpmnEvents`, which contain the name and type
of event and might be used to help determine this.

Once you have determined which workflow should receive the event, you can pass it to :code:`workflow.catch` to handle
it.

