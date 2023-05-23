SpiffWorkflow Concepts
======================

Specifications vs. Instances
----------------------------

SpiffWorkflow consists of two different categories of objects:

- **Specification objects**, which represent the definitions and derive from :code:`WorkflowSpec` and :code:`TaskSpec`
- **Instance objects**, which represent the state of a running workflow (:code:`Workflow`, :code:`BpmnWorkflow` and :code:`Task`)

In the workflow context, a specification is model of the workflow, an abstraction that describes *every path that could
be taken whenever the workflow is executed*.  An instance is a particular instantiation of a specification.  It describes *the
current state* or *the path(s) that were actually taken when the workflow ran*.

In the task context, a specification is a model for how a task behaves.  It describes the mechanisms for deciding *whether
there are preconditions for running an associated task*, *how to decide whether they are met*, and *what it means to complete
(successfully or unsuccessfully)*.  An instance describes the *state of the task, as it pertains to a particular workflow* and
*contains the data used to manage that state*.

Specifications are unique, whereas instances are not.  There is *one* model of a workflow, and *one* specification for a particular task.

Imagine a workflow with a loop.  The loop is defined once in the specification, but there can be many tasks associated with
each of the specs that comprise the loop.

In our BPMN example, described a product selection process.::

    Start -> Select and Customize Product -> Continue Shopping?

Since the customer can potentially select more than one product, how our instance looks depends on the customer's actions.  If
they choose three products, then we get the following tree::

    Start --> Select and Customize Product -> Continue Shopping?
          |-> Select and Customize Product -> Continue Shopping?
          |-> Select and Customize Product -> Continue Shopping?

There is *one* TaskSpec describing product selection and customization and *one* TaskSpec that determines whether to add more
items, but it may execute any number of imes, resulting in as many Tasks for these TaskSpecs as the number of products the
customer selects.

Understanding Task States
-------------------------

* **Predicted Tasks**

  A predicted task is one that will possibly, but not necessarily run at a future time.  For example, if a task follows a
  conditional gateway, which path is taken won't be known until the gateway is reached and the conditions evaluated.  There
  are two types of predicted tasks:

  - **MAYBE**: The task is part of a conditional path
  - **LIKELY** : The task is the default output on a conditional path

* **Definite Tasks**

  Definite tasks are certain to run as the workflow pregresses.

  - **FUTURE**: The task will definitely run.
  - **WAITING**: A condition must be met before the task can become **READY**
  - **READY**: The preconditions for running this task have been met
  - **STARTED**: The task has started running but has not finished

* **Finished Tasks**

  A finished task is one where no further action will be taken.

  - **COMPLETED**: The task finished successfully.
  - **ERROR**: The task finished unsucessfully.
  - **CANCELLED**: The task was cancelled before it ran or while it was running.

Tasks start in either a **PREDICTED** or **FUTURE** state, move through one or more **DEFINITE** states, and end in a
**FINISHED** state.  State changes are determined by several task spec methods:

* `_update_hook`: This method will be run by a task's predecessor when the predecessor completes.  The method checks the
  preconditions for running the task and returns a boolean indicating whether a task should become **READY**.  Otherwise,
  the state will be set to **WAITING**.

* `_on_ready_hook`: This method will be run when the task becomes **READY** (but before it runs).

* `run_hook`: This method implements the task's behavior when it is run, returning:

  - :code:`True` if the task completed successfully.  The state will transition to **COMPLETED**.
  - :code:`False` if the task completed unsucessfully.  The state will transition to **ERRROR**.
  - :code:`None` if the task has not completed.  The state will transition to **STARTED**.
  
* `_on_complete_hook`: This method will be run when the task's state is changed to **COMPLETED**.

* `_on_error_hook`: This method will be run when the task's state is changed to **ERROR**.

* `_on_trigger`: This method executes the task's behavior when it is triggered (`Trigger` tasks only).

Task Prediction
---------------

Each TaskSpec also has a `_predict_hook` method, which is used to set the state of not-yet-executed children.  The behavior
of `_predict_hook` varies by TaskSpec.  This is the mechanism that determines whether Tasks are **FUTURE**, **LIKELY**, or
**MAYBE**.  When a workflow is created, a task tree is generated that contains all definite paths, and branches of
**PREDICTED** tasks with a maximum length of two.  If a **PREDICTED** task becomes **DEFINITE**, the Task's descendants
are re-predicted.  If it's determined that a **PREDICTED** will not run, the task and all its descendants will be dropped
from the tree.  By default `_on_predict_hook` will ignore **DEFINITE** tasks, but this can be overridden by providing a
mask of `TaskState` values that specifies states other than **PREDICTED**.

Where Data is Stored
--------------------

Data can ba associated with worklows in the following ways:

- **Workflow data** is stored on the Workflow, with changes affecting all Tasks.
- **Task data** is local to the Task, initialized from the data of the Task's parent.
- **Task internal data** is local to the Task and not passed to the Task's children
- **Task spec data** is stored in the TaskSpec object, and if updated, the updates will apply to any Task that references the spec
  (unused by the :code:`bpmn` package and derivatives).

