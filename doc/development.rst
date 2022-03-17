SpiffWorkflow Concepts
====================================

Specification vs. Workflow Instance
-----------------------------------

One critical concept to know about SpiffWorkflow is the difference between a
:class:`SpiffWorkflow.specs.WorkflowSpec` and :class:`SpiffWorkflow.Workflow` and
the difference between a :class:`SpiffWorkflow.specs.TaskSpec` and :class:`SpiffWorkflow.Task`.

In order to understand how to handle a running workflow consider the following process::

    Choose product -> Choose amount -> Produce product A
                                  `--> Produce product B

As you can see, in this case the process resembles a simple tree. *Choose product*,
*Choose amount*, *Produce product A*, and *Produce product B* are all specific kinds
of *task specifications*, and the whole process is a *workflow specification*.

But when you execute the workflow, the path taken does not necessarily have the same shape. For example, if the user chooses to produce 3 items of product A, the path taken looks like the following::

    Choose product -> Choose amount -> Produce product A
                                  |--> Produce product A
                                  `--> Produce product A

This is the reason why you will find two different categories of objects in Spiff Workflow:

- **Specification objects** (WorkflowSpec and TaskSpec) represent the workflow definition, and
- **derivation tree objects** (Workflow and Task) model the task tree that represents the state of a running workflow.

Understanding task states
-------------------------

The following task states exist:

.. image:: figures/state-diagram.png

The states are reached in a strict order and the lines in the diagram show the possible state transitions.

The order of these state transitions is violated only in one case: A *Trigger* task may add additional work to a task that was already COMPLETED, causing it to change the state back to FUTURE.

- **MAYBE** means that the task will possibly, but not necessarily run at a future time. This means that it can not yet be fully determined as to whether or not it may run, for example, because the execution still depends on the outcome of an ExclusiveChoice task in the path that leads towards it.

- **LIKELY** is like MAYBE, except it is considered to have a higher probability of being reached because the path leading towards it is the default choice in an ExclusiveChoice task.

- **FUTURE** means that the processor has predicted that this this path will be taken and this task will, at some point, definitely run. (Unless the task is explicitly set to CANCELLED, which can not be predicted.) If a task is waiting on predecessors to run then it is in FUTURE state (not WAITING).

- **WAITING** means *I am in the process of doing my work and have not finished. When the work is finished, then I will be READY for completion and will go to READY state*. WAITING is an optional state.

- **READY** means "the preconditions for marking this task as complete are met".

- **COMPLETED** means that the task is done.

- **CANCELLED** means that the task was explicitly cancelled, for example by a CancelTask operation.

Associating data with a workflow
--------------------------------

The difference between *specification objects* and *derivation tree objects* is also important when choosing how to store data in a workflow. Spiff Workflow supports storing data in two ways:

- **Task spec data** is stored in the TaskSpec object. In other words, if a task causes task spec data to change, that change is reflected to all other instances in the derivation tree that use the TaskSpec object.
- **Task data** is local to the Task object, but is carried along to the children of each Task object in the derivation tree as the workflow progresses.

Internal Details
----------------

A **derivation tree** is created based off of the spec using a hierarchy of
:class:`SpiffWorkflow.Task` objects (not :class:`SpiffWorkflow.specs.TaskSpec` objects!).
Each Task contains a reference to the TaskSpec that generated it.

Think of a derivation tree as tree of execution paths (some, but not all, of
which will end up executing). Each Task object is basically a node in the
derivation tree. Each task in the tree links back to its parent (there are
no connection objects). The processing is done by walking down the
derivation tree one Task at a time and moving the task (and its
children) through the sequence of states towards completion.

You can serialize/deserialize specs. You can also
serialize/deserialize a running workflow (it will pull in its spec as well).

There's a decent eventing model that allows you to tie in to and receive
events (for each task, you can get event notifications from its TaskSpec).
The events correspond with how the processing is going in the derivation
tree, not necessarily how the workflow as a whole is moving.
See :class:`SpiffWorkflow.specs.TaskSpec` for docs on events.

You can nest workflows (using the :class:`SpiffWorkflow.specs.SubWorkflowSpec`).

The serialization code is done well which makes it easy to add new formats
if we need to support them.


Other documentation
-------------------

**API documentation** is currently embedded into the Spiff Workflow source code and not yet made available in a prettier form.

If you need more help, please create an issue in our
`issue tracker <https://github.com/knipknap/SpiffWorkflow/issues>`_.
