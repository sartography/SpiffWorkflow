Overview
========

This section focuses on the example application rather than the library itself; it is intended to orient people
attempting to use this documentation, so we won't devote that much space to it (much of it is necessary for a 
functioning app, but not directly relevant to library use); nonetheless, there is quite a bit of code and a general
idea of what's here will be helpful.

The application has several parts:

- an engine, which uses SpiffWorkflow to run, parse, and serialize workflows
- a curses UI for running and examining Workflows, which uses the engine
- a command line UI with some limited functionality, which also uses the engine

We'll mainly focus on the engine, as it contains the interface with the library, though a few examples will come from
the other components.  The engine is quite small and simple compared to the code required to handle user input and
display information in a terminal.

.. warning::

    This application is *not* a robust application and won't be suitable for displaying large amounts of data, which
    may cause it to crash.  The application won't run unless your terminal is at least 13 lines high.  It also may
    randomly crash at other times as well.  While I'll make improvements as I add more examples and bug reports and/or
    fixes are always welcome, my focus is on using the library rather than the UI.

Configuration is set up in a python module and passed into the application with the `-e` argument, which loads the
configured engine from this file.  This setup should make it relatively to change the behavior of engine.  The
following configurations are included:

- :code:`spiff_example.spiff.file`: uses spiff BPMN extensions and serializes to JSON files
- :code:`spiff_example.spiff.sqlite`: uses spiff BPMN extensions and serializes to SQLite
- :code:`spiff_example.camunda.default`: uses Camunda extensions and serializes to SQLite

.. _quickstart:

Quickstart
==========

There are several versions of a product ordering process of variying complexity located in the
:example:`bpmn/tutorial` directory of the repo which contain most of the elements that SpiffWorkflow supports.  These
diagrams can be viewed in any BPMN editor, but many of them have custom extensions created with
`bpmn-js-spiffworflow <https://github.com/sartography/bpmn-js-spiffworkflow>`_.

To add a workflow via the command line and store serialized specs in JSON files:

.. code-block:: console

   ./runner.py -e spiff_example.spiff.file add \
      -p order_product \
      -b bpmn/tutorial/{top_level,call_activity}.bpmn \
      -d bpmn/tutorial/{product_prices,shipping_costs}.dmn

To run the curses application using serialized JSON files:

.. code-block:: console

   ./runner.py -e spiff_example.spiff.file

Select the 'Start Workflow' screen and start the process.

The Application in Slightly More Depth
======================================

The application requires the name of a module to load that contains a configuration such as one of those defined above.

To start the curses UI using the JSON file serializer:

.. code-block:: console

   ./runner.py -e spiff_example.spiff.file

If the application is run with no other arguments, the curses UI will be loaded.

It is possible to add a workflow spec through the curses UI, but it is going to be somewhat painful to do so unless
you are a better typist and proofreader than I; therefore, there are also a few command line utilities for handling
some of the functionality, including adding workflow specs.

Command line options are

- :code:`add` to add a workflow spec (while taking advantage of your shell's file completion functionality)
- :code:`list` to list the available specs
- :code:`run` to run a workflow non-interactively

Each of these options has a help menu that describes how to use them.

Configuration Modules
=====================

The three main ways that users can customize the library are:

- the parser
- the script engine
- the serializer

We use the configuration module to allow these components to be defined outside the workflow engine itself and passed
in as parameters to make it easier to experiment. I am somewhat regularly asked questions about why a diagram doesn't
executed as expected, or how to get the script engine to work a particular way; this is a first pass at setting
something up that works better for me than configuring the library's test loader and running that in a debugger; I hope
other people will find it useful as well.

We'll go through the configuration in greater detail in later sections, but we'll take a brief look at the simplest
configuration, :app:`spiff/file.py` here.

In this file, we'll initialize our parser:

.. code-block:: python

    parser = SpiffBpmnParser()

We don't need to further customize this parser -- this is a builtin parser that can handle DMN files as well as Spiff
BPMN extensions.

We also need to initialize a serializer:

.. code-block:: python

    dirname = 'wfdata'
    FileSerializer.initialize(dirname)
    registry = FileSerializer.configure(SPIFF_CONFIG)
    serializer = FileSerializer(dirname, registry=registry)

JSON specs and workflows will be stored in :code:`wfdata`.  The :code:`registry` is the place where information about
converting Python objects to and from JSON-serializable dictionary form is maintained.  :code:`SPIFF_CONFIG` tells the
serializer how to handle objects used internally by Spiff.  Workflows can also contain arbitrary data, so this registry
can also tell the serializer how to handle any non-serializable data in your workflow.  We'll go over this in more
detail in :ref:`serializing_custom_objects`.

We initialize a scripting enviroment:

.. code-block:: python

    script_env = TaskDataEnvironment({'datetime': datetime })
    script_engine = PythonScriptEngine(script_env)

The :code:`PythonScriptEngine` handles execution of script tasks and evaluation of gateway and DMN conditions.
We'll create the script engine based on it; execution and evaluation will occur in the context of this enviroment.

SpiffWorkflow provides a default scripting environment that is suitable for simple applications, but a serious
application will probably need to extend (or restrict) it in some way.  See :doc:`script_engine` for a few examples.
Therefore, we have the ability to optionally pass one in.

In this case, we'll include access to the :code:`datetime` module, because we'll use it in several of our script tasks.

We also specify some handlers:

.. code-block:: python

    handlers = {
        UserTask: UserTaskHandler,
        ManualTask: ManualTaskHandler,
        NoneTask: ManualTaskHandler,
    }

This is a mapping of task spec to task handler and lets our application know how to handle these tasks.

.. note::

    In our application, we're also passing in handlers, but this is not a typical use case.  The library knows how to
    handle all task types except for human (User and Manual) tasks, and those handlers would typically be built into
    your application.  However, this application needs to be able to deal with more than one set of human task specs,
    and this is a convenient way to do this.  The library treats None tasks (tasks with no specific type assigned)
    like Manual Tasks by default.

We then create our BPMN engine (:app:`engine/engine.py`) using each of these components:

.. code-block:: python

    from ..engine import BpmnEngine
    engine = BpmnEngine(parser, serializer, script_env)

The handlers are automatically passed to the curses UI by the main runner.
