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
