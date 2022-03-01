MultiInstance Tasks
===================

BPMN Model
----------

We'll be using the the `transaction 
<https://github.com/sartography/SpiffExample/bpmn/multiinstance.bpmn>`_ and
`call activity <https://github.com/sartography/SpiffExample/bpmn/call_activity_multi.bpmn>`_
workflows, as well as the `product_prices 
<https://github.com/sartography/SpiffExample/bpmn/product_prices.dmn>`_
and `shipping_costs <https://github.com/sartography/SpiffExample/bpmn/shipping_costs.dmn>`_
DMN tables from `SpiffExample <https://github.com/sartography/SpiffExample>`_.

Suppose we want our customer to be able to select more than one product.

If we knew how many products they would select at the beginning of the workflow, we could
configure 'Select and Customize Product' as a Sequential MultiInstance Task.  We would
specify the name of the collection and each iteration of the task would add a new item
to it.

We'll need to modify that workflow to ask them whether they want to continue shopping and 
maintain their product selections in a collection.

.. figure:: figures/call_activity_multi.png
   :scale: 30%
   :align: center

   Selecting more than one product

.. figure:: figures/documentation_multi.png
   :scale: 30%
   :align: center

   Updated Documentation for 'Review Order'

Parallel MultiInstance
^^^^^^^^^^^^^^^^^^^^^^

We'll also update our 'Retrieve Product' task and 'Product Not Available' flows to 
accommodate multiple products.  We can use a Parallel Multiinstance for this, since
it does not matter what order our Employee retrieves the products in.

.. figure:: figures/multiinstance_task_configuration.png
   :scale: 30%
   :align: center

   MultiInstance task configuration

We will generate a task for each of the items in the collection.  Because of the way
SpiffWorkflow manages the data for these tasks, the collection MUST be a dictionary.

Each value os the dictionary will be copied into a variable with the name specified in
the 'Element Variable' field, so you'll need to specify this as well.

.. figure:: figures/multiinstance_form_configuration.png
   :scale: 30%
   :align: center

   MultiInstance form configuration

We'll also need to update the form field id so that the results will be added to the
item of the collection rather than the top level of the task data.  This is where the
'Element Variable' field comes in: we'll need to change `product_avaliable` to
`product.product_available`, because we set up `product` as our reference to the 
current item.

.. figure:: figures/multiinstance_flow_configuration.png
   :scale: 30%
   :align: center

   MultiInstance task configuration

Finally, we'll need to update our 'No' flow to check all items in the collection for
availability.

.. note::

   In our form configuration, we used `product.product_available` but when we reference
   it in the flow, we use the standard python dictionary syntax.  We can't use that
   notation when defining a form field, so internally, Spiff will generate a dot notation
   representation of a dictionary so that nested structures may be referenced in
   form fields.

Sequential MultiInstance
^^^^^^^^^^^^^^^^^^^^^^^^

SpiffWorkflow also supports Sequential MultiInstance Tasks for previously defined
collections, or if the loopCardinality is known in advance, although we have not added an
example of this to our workflow.

For more information about MultiInstance Tasks and SpiffWorkflow, see the 
Advanced Features Section.

Running The Model
-----------------

If you have set up our example repository, this model can be run with the
following command:

.. code-block:: console

   ./run.py -p order_product \
        -d bpmn/product_prices.dmn bpmn/shipping_costs.dmn \
        -b bpmn/multiinstance.bpmn bpmn/call_activity_multi.bpmn

