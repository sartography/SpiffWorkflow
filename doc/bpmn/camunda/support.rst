Camunda Editor Support
======================

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


.. toctree::
   :maxdepth: 3

   tasks
   events
   multiinstance
