Modules
=======

SpiffWorkflow consists several modules.  The modules included in this package and reasons for its structure are historical.
The library originally consisted of only the core library specs; it was later extended to provide BPMN support (in a way
that did not entirely fit in with the operation of the original library); then this BPMN support was further refined to
provide support for custom extensions to the BPMN spec.  Recent redevlopment has mainly focused on BPMN, with minimal
changes to the core library.  Therefore there are fairly significant differences between the BPMN and non-BPMN parts of the
library.  We're working towards making these consistent!

The Core Library
----------------

The core library provides basic implementations of a large set of task spec types and basic workflow execution
capabilities.

- Specs implementations are in :code:`specs`
- Workflow implementation is in :code:`workflow.py`
- Task implementation is in :code:`task.py`, with utilities for iteration and filtering in :code:`util.task.py`

It is documented in :doc:`core/index`.

Generic BPMN Implementation
---------------------------

This module extends the core implementation to support the parsing and execution of BPMN diagrams.

- The base specs of the core library are extended to implement generic BPMN attributes and behavior in
  :code:`bpmn.specs`.  Task specs are extended in two ways: to provide generic behavior common to all BPMN tasks
  (:code:`bpmn.specs.mixins.bpmn_spec_mixin.BpmnSpecMixin`) and type-specific behavior (other task specs in
  :code:`bpmn.specs.mixins`).  The reason is to allow either category of properties to be extended separately.
- The workflow implementation in the BPMN package handles subworkflows in an entirely different way from the core
  library.  It also allows for filtering on and iterating over tasks with certain BPMN attributes.
- A workflow has a scripting environment, in which task specific code will be executed (in the core library, this
  would be accomplished through an execute task that spawns a subprocess or a custom task spec).
- The serializer has been completely replaced.

This module is documented in :doc:`bpmn/index`.

Spiff BPMN Extensions
---------------------

This module extends the generic BPMN implementation with support for custom extensions used by
`Spiff Arena <https://spiff-arena.readthedocs.io/en/latest/>`_.

Camunda BPMN Extensions
-----------------------

This module extends the generic BPMN implementation with limited support for Camunda extensions.

.. warning::

    The Camunda package is not under development.  We'll accept contributions from Camunda users, but we are not
    actively maintaining this package.
