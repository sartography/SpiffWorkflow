Creating and Running Workflows
==============================

.. code-block:: python

    from SpiffWorkflow.bpmn import BpmnWorkflow, BpmnEvent
    from SpiffWorfkflow import TaskState

Parsing
=======

Basic Parsing
-------------

.. code-block:: python

    from SpiffWorkflow.bpmn.parser import BpmnParser, BpmnValidator

Customized Parsing
------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.parser import TaskParser, EventDefinitionParser

Examples
--------

- :doc:`parsing`
- :doc:`custom_task_spec`

Script Engine
=============

To modify the default execution environment
-------------------------------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

To control how the engine interacts with the workflow
-----------------------------------------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.script_engine import PythonScriptEngine

To implement custom exec/eval
-----------------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.script_engine import BasePythonScriptEngineEnvironment

Examples
--------

- :doc:`script_engine`

Specs
=====

Using a Spec
------------

.. code-block:: python

    from SpiffWorkflow.bpmn.specs import <TaskSpec>
    from SpiffWorkflow.bpmn.specs.event_definition import <EventDefinition>

Extending a Spec
----------------

.. code-block:: python

    from SpiffWorkflow.bpmn.specs import BpmnTaskSpec           # Implements generic BPMN behavior
    from SpiffWorkflow.bpmn.specs.mixins import <TaskSpecMixin> # Implements specific BPMN behavior

Implement a Datastore
---------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.spec import BpmnDataStoreSpecification

Examples
--------

- :doc:`workflows`
- :doc:`custom_task_spec`

Serializer
==========

Basic Usage
-----------

.. code-block:: python

    from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer

Custom Data
-----------

.. code-block:: python

    from SpiffWorkflow.bpmn.serializer import DefaultRegistry

Spec Customizations
-------------------

.. code-block:: python

    from SpiffWorkflow.bpmn.serializer import DEFAULT_CONFIG
    from SpiffWorkflow.bpmn.serializer.default import <TaskSpecConverter>
    from SpiffWorkflow.bpmn.serializer.helpers import (
        TaskSpecConverter,
        EventDefinitionConverter,
        BpmnDataSpecificationConverter,
    )

Examples
--------

- :doc:`serialization`
- :doc:`custom_task_specs`

DMN
===

.. code-block:: python

    from SpiffWorkflow.dmn.parser import BpmnDmnParser
    from SpiffWorkflow.dmn.specs import BusinessRuleTaskMixin
    from SpiffWorkflow.dmn.serializer import BaseBusinessRuleTaskConverter

Spiff
=====

.. code-block:: python

    from SpiffWorkflow.spiff.parser import SpiffBpmnParser, VALIDATOR
    from SpiffWorkflow.spiff.specs import <TaskSpec>
    from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG

Camunda
=======

.. code-block:: python

    from SpiffWorkflow.camunda.parser import CamundaParser
    from SpiffWorkflow.camunda.specs import <TaskSpec>
    from SpiffWorkfllw.camunda.serializer import DEFAULT_CONFIG

