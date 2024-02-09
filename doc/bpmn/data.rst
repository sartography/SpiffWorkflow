Data
====

Data Objects
------------

Data Objects exist at the process level and are not visible to individual Tasks unless explicitly indicated (ie there
is a line from the Data Object to or from a Task).

All Workflows have a :code:`data` attribute; like :code:`Task.data`, it is just a dictionary, and this is where the
values for Data Objects are stored.

If a Data Object is to be made available to a Task, the value is copied from the Workflow data into the Task data
immediately before the Task becomes :code:`READY`; when the Task completes, the Data Object value is removed from the
Task data.

If value is to be written to a Data Object, it is stored in the Workflow data and removed from the Task data when the
Task completes.

Data Objects are always available to Gateways (even though you cannot draw a line on the diagram).

Data Inputs and Outputs
-----------------------

In complex workflows, it is useful to be able to specify required Data Inputs and Outputs, especially for Call Activities
given that they are external and might be shared across many different processes.

When you add a Data Input to a Call Activity, SpiffWorkflow will check that a variable with that name is available to
be copied into the activity and copy *only* the variables you've specified as inputs.  When you add a Data Output,
SpiffWorkflow will copy *only* the variables you've specified from the Call Activity at the end of the process.  If any
of the variables are missing, SpiffWorkflow will raise an error.

Our product customization Call Activity (:bpmn:`call_activity.bpmn`) does not require any input, but the output of the
process is the product name and quantity.  We can add corresponding Data Outputs for those.

If you use the alternate version of this Call Activity (:bpmn:`data_output.bpmn`) and choose a product that has
customizations, when you inspect the data after the Call Activity completes, you'll see that the customizations have been
removed.

To load this example (product D has two customizations):

.. code-block:: console

    ./runner.py -e spiff_example.spiff.file add -p order_product \
        -b bpmn/tutorial/{top_level,data_output}.bpmn \
        -d bpmn/tutorial/{shipping_costs,product_prices}.dmn

.. note::

   The BPMN spec allows *any* task to have Data Inputs and Outputs. Our modeler does not provide a way to add them to
   arbitrary tasks, but SpiffWorkflow will recognize them on any task if they are present in the BPMN XML.

