Tasks
=====

User Tasks
----------

Creating a User Task
^^^^^^^^^^^^^^^^^^^^

When you click on a user task in a BPMN modeler, the Properties Panel includes a form tab. Use this
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

Running The Model
-----------------

If you have set up our example repository, this model can be run with the
following command:

.. code-block:: console

   ./camunda-bpmn-runner.py -p order_product -d bpmn/camunda/product_prices.dmn -b bpmn/camunda/task_types.bpmn

Example Application Code
------------------------

Handling the User Task
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    dct = {}
    for field in task.task_spec.form.fields:
        if isinstance(field, EnumFormField):
            option_map = dict([ (opt.name, opt.id) for opt in field.options ])
            options = "(" + ', '.join(option_map) + ")"
            prompt = f"{field.label} {options} "
            option = input(prompt)
            while option not in option_map:
                print(f'Invalid selection!')
                option = input(prompt)
            response = option_map[option]
        else:
            response = input(f"{field.label} ")
            if field.type == "long":
                response = int(response)
        update_data(dct, field.id, response)
    DeepMerge.merge(task.data, dct)

The list of form fields for a task is stored in :code:`task.task_spec.form_fields`.

For Enumerated fields, we want to get the possible options and present them to the
user.  The variable names of the fields were stored in :code:`field.id`, but since
we set labels for each of the fields, we'd like to display those instead, and map
the user's selection back to the variable name.

For other fields, we'll just store whatever the user enters, although in the case
where the data type was specified to be a :code:`long`, we'll convert it to a
number.

Finally, we need to explicitly store the user-provided response in a variable
with the expected name with :code:`update_data(dct, field.id, response)` and merge
the newly collected data into our task data with :code:`DeepMerge.merge(task.data, dct)`.

Our :code:`update_data` function handles "dot notation" in field names, which creates
nested dictionaries based on the path components.

.. code:: python

    def update_data(dct, name, value):
        path = name.split('.')
        current = dct
        for component in path[:-1]:
            if component not in current:
                current[component] = {}
            current = current[component]
        current[path[-1]] = value
