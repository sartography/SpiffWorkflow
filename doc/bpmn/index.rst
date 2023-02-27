BPMN Workflows
==============

The basic idea of SpiffWorkflow is that you can use it to write an interpreter
in Python that creates business applications from BPMN models.  In this section,
we'll develop a model of an example process and as well as a
simple workflow runner.

We expect that readers will fall into two general categories:

- People with a background in BPMN who might not be very familiar Python
- Python developers who might not know much about BPMN

This section of the documentation provides an example that (hopefully) serves
the needs of both groups.  We will introduce the BPMN elements that SpiffWorkflow
supports and show how to build a simple workflow runner around them.

SpiffWorkflow does heavy-lifting such as keeping track of task dependencies and
states and providing the ability to serialize or deserialize a workflow that
has not been completed.  The developer will write code for displaying workflow
state and presenting tasks to users of their application.

All the Python code and BPMN models used here are available in an example
project called `spiff-example-cli <https://github.com/sartography/spiff-example-cli>`_.

Quickstart
----------

Check out the code in `spiff-example-cli <https://github.com/sartography/spiff-example-cli>`_
and follow the instructions to set up an environment to run it in.

Run the sample workflow we built up using our example application with the following
command:

.. code-block:: console

   ./run.py -p order_product \
        -d bpmn/{product_prices,shipping_costs}.dmn \
        -b bpmn/{multiinstance,call_activity_multi}.bpmn


For a full description of program options:

.. code-block:: console

   ./run.py --help

The code in the workflow runner and the models in the bpmn directory of the
repository will be discussed in the remainder of this tutorial.

Supported BPMN Elements
-----------------------

.. toctree::
   :maxdepth: 3

   tasks
   gateways
   organization
   events
   multiinstance
   spiff-extensions

Putting it All Together
-----------------------

.. toctree::
   :maxdepth: 2

   synthesis

Features in More Depth
----------------------

.. toctree::
   :maxdepth: 2

   advanced
