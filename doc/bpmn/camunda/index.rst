Using the Camunda Configuration Module
======================================

.. warning:: There is a better way ...
  SpiffWorkflow does not aim to support all of Camunda's proprietary extensions.
  Many of of the items in the Camunda Properties Panel do not work.  And
  major features of SpiffWorkflow (Messages, Data Objects, Service Tasks, Pre-Scripts, etc...)
  can not be configured in the Camunda editor.  Use `SpiffArena <https://www.spiffworkflow.org/posts/articles/get_started/>`_
  to build and test your BPMN models instead!

Earlier users of SpiffWorkflow relied heavily on Camunda's modeler and several of our task spec
implementations were based on Camunda's extensions.  Support for these extensions has been moved
to the :code:`camunda` package.  We are not actively maintaining this package (though we will
accept contributions from Camunda users!).  Please be aware that many of the Camunda extensions
that will appear in the Camunda editor do not work with SpiffWorkflow.

In this repo, we provide the following configuration:

.. code-block:: console

   ./runner.py -e spiff_example.camunda.sqlite

Tasks
=====

User Tasks
----------

Creating a User Task
^^^^^^^^^^^^^^^^^^^^

When you click on a user task in the BPMN modeler, the Properties Panel includes a form tab. Use this
tab to build your questions.

The following example shows how a form might be set up in Camumda.

.. figure:: figures/user_task.png
   :scale: 30%
   :align: center

   User Task configuration


Manual Tasks
------------

Creating a Manual Task
^^^^^^^^^^^^^^^^^^^^^^

We can use the BPMN element Documentation field to display more information about the context of the item.

Spiff is set up in a way that you could use any templating library you want, but we have used 
`Jinja <https://jinja.palletsprojects.com/en/3.0.x/>`_.

In this example, we'll present an order summary to our customer.

.. figure:: figures/documentation.png
   :scale: 30%
   :align: center

   Element Documentation

Example Code
------------

Example Human task handlers can be found in :app:`camunda/curses_handlers.py`.

Events
======

Message Events
--------------

Configuring Message Events
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: figures/throw_message_event.png
   :scale: 60%
   :align: center

   Throw Message Event configuration


.. figure:: figures/message_start_event.png
   :scale: 60%
   :align: center

   Message Catch Event configuration

The Throw Message Event Implementation should be 'Expression' and the Expression should
be a Python statement that can be evaluated.  In this example, we'll just send the contents
of the :code:`reason_delayed` variable, which contains the response from the 'Investigate Delay'
Task.

We can provide a name for the result variable, but I have not done that here, as it does not
make sense to me for the generator of the event to tell the handler what to call the value.
If you *do* specify a result variable, the message payload (the expression evaluated in the
context of the Throwing task) will be added to the handling task's data in a variable of that
name; if you leave it blank, SpiffWorkflow will create a variable of the form <Handling
Task Name>_Response.

MultiInstance Tasks
===================

Earlier versions of SpiffWorkflow relied on the properties available in the Camunda MultiInstance Panel.

.. figure:: figures/multiinstance_task_configuration.png
   :scale: 60%
   :align: center

   MultiInstance Task configuration

SpiffWorkflow has a MultiInstance Task spec in the :code:`camunda` package that interprets these fields
in the following way:

* Loop Cardinality:

   - If this is an integer, or a variable that evaluates to an integer, this number would be 
     used to determine the number of instances
   - If this is a collection, the size of the collection would be used to determine the number of
     instances

* Collection: the output collection (input collections have to be specified in the "Cardinality" field).

* Element variable: the name of the varible to copy the item into for each instance.

.. warning::

   The spec in this package is based on an old version of Camunda, so the panel may have changed.  The
   properties might or might not have been the way Camunda used these fields, and may or may not be similar
   to newer or current versions.  *Use at your own risk!*
