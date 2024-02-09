Script Engine Overview
======================

You may need to modify the default script engine, whether because you need to make additional
functionality available to it, or because you might want to restrict its capabilities for
security reasons.

.. warning::

   By default, the scripting environment passes input directly to :code:`eval` and :code:`exec`!  In most
   cases, you'll want to replace the default scripting environment with one of your own.

Restricting the Script Environment
==================================

The following example replaces the default global enviroment with the one provided by
`RestrictedPython <https://restrictedpython.readthedocs.io/en/latest/>`_

We've modified our engine configuration to use the restricted environment in :app:`spiff/restricted.py`

.. code:: python

    from RestrictedPython import safe_globals
    from SpiffWorkflow.bpmn.PythonScriptEngineEnvironment import TaskDataEnvironment

    restricted_env = TaskDataEnvironment(safe_globals)
    restricted_script_engine = PythonScriptEngine(environment=restricted_env)

We've also included a dangerous process in :bpmn:`dangerous.bpmn`

If you run this process using the regular script enviromment, the BPMN process will get the OS process ID and
prompt you to kill it; if you answer 'Y', it will do so (it won't actually do anything more dangerous than screw
up your terminal settings, but hopefully proves the point).

.. code-block:: console

    ./runner.py -e spiff_example.spiff.file add -p end_it_all -b bpmn/tutorial/dangerous.bpmn
    ./runner.py -e spiff_example.spiff.file

If you load the restricted engine:

.. code-block:: console

    ./runner.py -e spiff_example.spiff.restricted

You'll get an error, because imports have been restricted.

.. note::

    Since we used exactly the same parser and serializer, we can simply switch back and forth between these
    two script engines (that is the only difference between the two configurations).

Making Custom Classes and Functions Available
=============================================

Another reason you might want to customize the scripting environment is to provide access to custom
classes or functions.

In many of our example models, we use DMN tables to obtain product information.  DMN is a convenient
way of making table data available to our processes.

However, in a slightly more realistic scenario,  we would surely have information about how the product
could be customized in a database somewhere.  We would not hard code product information in our diagram
(although it is much easier to modify the BPMN and DMN models than to change the code itself!).  Our
shipping costs would not be static, but would depend on the size of the order and where it was being
shipped -- maybe we'd query an API provided by our shipper.

SpiffWorkflow is obviously **not** going to know how to query **your** database or make API calls to
**your** vendors.  However, one way of making this functionality available inside your diagram is to
implement the calls in functions and add those functions to the scripting environment, where they
can be called by Script Tasks.

We are not going to actually include a database or API and write code for connecting to and querying
it, but since we only have 7 products we can model our database with a simple dictionary lookup
and just return the same static info for shipping for the purposes of the tutorial.

We'll customize our scripting environment in :app:`spiff/custom_object.py`:

.. code:: python

    from collections import namedtuple

    ProductInfo = namedtuple('ProductInfo', ['color', 'size', 'style', 'price'])
    INVENTORY = {
        'product_a': ProductInfo(False, False, False, 15.00),
        'product_b': ProductInfo(False, False, False, 15.00),
        'product_c': ProductInfo(True, False, False, 25.00),
        'product_d': ProductInfo(True, True, False, 20.00),
        'product_e': ProductInfo(True, True, True, 25.00),
        'product_f': ProductInfo(True, True, True, 30.00),
        'product_g': ProductInfo(False, False, True, 25.00),
    }

    def lookup_product_info(product_name):
        return INVENTORY[product_name]

    def lookup_shipping_cost(shipping_method):
        return 25.00 if shipping_method == 'Overnight' else 5.00

    script_env = TaskDataEnvironment({
        'datetime': datetime,
        'lookup_product_info': lookup_product_info,
        'lookup_shipping_cost': lookup_shipping_cost,
    })
    script_engine = PythonScriptEngine(script_env)

.. note::

    We're also adding :code:`datetime`, because other parts of the process require it.

We can use the custom functions in script tasks like any normal function.  To load the example diagrams that use the
custom script engine:

.. code-block:: console

    ./runner.py -e spiff_example.spiff.custom_object add -p order_product \
        -b bpmn/tutorial/{top_level_script,call_activity_script}.bpmn

If you start the application in interactive mode and choose a product, you'll see tuple info reflected in the task data
after selecting a product.

Service Tasks
=============

We can also use Service Tasks to accomplish the same goal. Service Tasks are also executed by the workflow's script
engine, but through a different method, with the help of some custom extensions in the :code:`spiff` module:

- `operation_name`, the name assigned to the service being called
- `operation_params`, the parameters the operation requires

The advantage of a Service Task is that it is a bit more transparent what is happening (at least at a conceptual level)
than function calls embedded in a Script Task.

We implement the :code:`PythonScriptEngine.call_service` method in :app:`spiff/service_task.py`:

.. code:: python

    service_task_env = TaskDataEnvironment({
        'product_info_from_dict': product_info_from_dict,
        'datetime': datetime,
    })

    class ServiceTaskEngine(PythonScriptEngine):

        def __init__(self):
            super().__init__(environment=service_task_env)

        def call_service(self, operation_name, operation_params, task_data):
            if operation_name == 'lookup_product_info':
                product_info = lookup_product_info(operation_params['product_name']['value'])
                result = product_info_to_dict(product_info)
            elif operation_name == 'lookup_shipping_cost':
                result = lookup_shipping_cost(operation_params['shipping_method']['value'])
            else:
                raise Exception("Unknown Service!")
            return json.dumps(result)

    service_task_engine = ServiceTaskEngine()

Instead of adding our custom functions to the environment, we'll override :code:`call_service` and call them directly
according to the `operation_name` that was given.  The :code:`spiff` Service Task also evaluates the parameters
against the task data for us, so we can pass those in directly.  The Service Task will also store our result in
a user-specified variable.

We need to send the result back as json, so we'll reuse the functions we wrote for the serializer (see
:ref:`serializing_custom_objects`).

The Service Task will assign the dictionary as the operation result, so we'll add a `postScript` to the Service Task
that retrieves the product information that creates a :code:`ProductInfo` instance from the dictionary, so we need to
add that to the scripting enviroment too.

The XML for the Service Task looks like this:

.. code:: xml

    <bpmn:serviceTask id="Activity_1ln3xkw" name="Lookup Product Info">
      <bpmn:extensionElements>
        <spiffworkflow:serviceTaskOperator id="lookup_product_info" resultVariable="product_info">
          <spiffworkflow:parameters>
            <spiffworkflow:parameter id="product_name" type="str" value="product_name"/>
          </spiffworkflow:parameters>
        </spiffworkflow:serviceTaskOperator>
        <spiffworkflow:postScript>product_info = product_info_from_dict(product_info)</spiffworkflow:postScript>
      </bpmn:extensionElements>
      <bpmn:incoming>Flow_104dmrv</bpmn:incoming>
      <bpmn:outgoing>Flow_06k811b</bpmn:outgoing>
    </bpmn:serviceTask>

Getting this information into the XML is a little bit beyond the scope of this tutorial, as it involves more than
just SpiffWorkflow.  I hand edited it for this case, but you can hardly ask your BPMN authors to do that!

Our `modeler <https://github.com/sartography/bpmn-js-spiffworkflow>`_ has a means of providing a list of services and
their parameters that can be displayed to a BPMN author in the Service Task configuration panel.  There is an example of
hard-coding a list of services in
`app.js <https://github.com/sartography/bpmn-js-spiffworkflow/blob/0a9db509a0e85aa7adecc8301d8fbca9db75ac7c/app/app.js#L47>`_
and as suggested, it would be reasonably straightforward to replace this with a API call.  
`SpiffArena <https://www.spiffworkflow.org/posts/articles/get_started/>`_ has robust mechanisms for handling this that
might serve as a model for you.

How this all works is obviously heavily dependent on your application, so we won't go into further detail here, except
to give you a bare bones starting point for implementing something yourself that meets your own needs.

To run this workflow:

.. code-block:: console

    ./runner.py -e spiff_example.spiff.service_task add -p order_product \
        -b bpmn/tutorial/{top_level_service_task,call_activity_service_task}.bpmn

