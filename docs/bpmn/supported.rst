List of Supported Elements
==========================

Tasks
-----

* User Task
* Manual Task
* Business Rule Task
* Script Task
* Service Task

.. note::

    Spiff's implementation of Service Tasks is abstract, so while they will be parsed, the
    library provides no built-in mechanism for executing them.

Gateways
--------

* Parallel Gateway
* Exclusive Gateway
* Inclusive Gateway
* Event-Based Gateway

Subrocesses and Call Activities
-------------------------------

* Subprocess
* Call Activity
* Transaction Subprocess
* Event Subprocess
* Ad Hoc Subprocess (experimental)

.. note::

    Ad Hoc Subprocesses are neither particularly well defined in the BPMN spec, nor
    well-suited to the execution model of this library.

    The BPMN spec authors have this to say:

    "It is a challenge for a BPM engine to monitor the status of Ad-Hoc Sub-Processes, 
    usually these kind of Processes are handled through groupware applications (such as e-mail),
    but BPMN allows modeling of Processes that are not necessarily executable, although there 
    are some process engines that can follow an Ad-Hoc Sub-Process."

    This library organizes tasks in a tree, with children inheriting data from their parents,
    and needless to say this is difficult when tasks aren't connected in a meaningful way.

    The general operation of this subprocess type is as follows:

    * Data is maintained at the workflow level
    * Whenever a fragment completes, this data is updated
    * If any tasks or gateways have conditions associated with them, they will be triggered if the
      condition is met when evaluated against the current state of the data
    * Tasks with no conditions are automatically started when the workflow begins and are only
      completed once
    * Once a task starts, its data generally will not be updated; updates are only made when
      triggering tasks.  If the data of a multi-instance or loop tasks changes mid-execution,
      you will likely be in a world of pain.

    Data management is going to be quite difficult, as it is very easy to overwrite updated
    data with older data.  For example, suppose you have two independent tasks modifying
    different parts of the data.  Whichever one completes later will overwrite the data 
    set by the first task.  So you will have to be *very* careful to remove un-needed data
    from individual tasks.  Using data objects may alleviate the problem (they cause copying
    values into and out of a task when the task runs), but there is still the potential of two
    tasks reading/writing to the same data object.  Such are the pitfalls of a global state.

    Use this task type with caution!


Events
------

* Cancel Event
* Escalation Event
* Error Event
* Message Event
* Signal Event
* Terminate Event
* Timer Event

Data
----

* Data Object
* Data Store

.. note::

    Spiff's Data Store implementation is abstract; Spiff can parse a Data Store, but does not
    provide any built-in mechanism for reading and writing to it.

Loops
-----

* Loop Task
* Parallel MultiInstance Task
* Sequential MultiInstance Task


.. note::

    Parallel MultiInstance tasks are *not* executed by SpiffWorkflow in parallel.  SpiffWorkflow
    merely indicates that parallel tasks become ready at the same time and that the workflow
    engine may execute them in parallel.
