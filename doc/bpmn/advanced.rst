A More In-Depth Look at Some of SpiffWorkflow's Features
========================================================

Working With Lanes
------------------

In our earlier example, all we did was check the lane a task was in and display
it along with the task name and state.

Lets take a look at a sample workflow with lanes:

.. figure:: figures/lanes.png
   :scale: 30%
   :align: center

   Workflow with lanes

To get all of the tasks that are ready for the 'Customer' workflow, we could 
specify the lane when retrieving ready user tasks:

.. code:: python

     ready_tasks = workflow.get_ready_user_tasks(lane='Customer')

If there were no tasks ready for the 'Customer' lane, you would get an empty list, 
and of course if you had no lane that was labeled 'Customer' you would *always* get an 
empty list.

Nav(igation) List
-----------------

.. sidebar:: Warning!

  At the time of writing, the nav list does have some issues. The main issue is that there are 'issues' with showing
  the tasks for a subprocess. For most self-contained workflows, the nav-list does a good job of showing all of the
  events that are coming up and where a user is at in the process. Another set of features that have not been tested
  with the navigation list are any kind of boundary events which may cause a non-linear flow which would be hard to
  render.

It is usually the case that it will be necessary to present the user with an overview of
the workflow state as a whole.  SpiffWorkflow provides a "Navigation List" with a more
user-friendly presentation of upcoming tasks.

In order to get the navigation list, we can call the workflow.get_nav_list() function. This 
will return a list of dictionaries with information about each task and decision point in the 
workflow. Each item in this list returns some information about the tasks that are in the workflow, 
and how it relates to the other tasks.

To give you an idea of what is in the list I'll include a segment from the documentation::

               id               -   TaskSpec or Sequence flow id
               task_id          -   The uuid of the actual task instance, if it exists.
               name             -   The name of the task spec (or sequence)
               description      -   Text description
               backtracks       -   Boolean, if this backtracks back up the list or not
               level            -   Depth in the tree - probably not needed
               indent           -   A hint for indentation
               child_count       -   The number of children that should be associated with
                                    this item.
               lane             -   This is the swimlane for the task if indicated.
               state            -   Text based state (may be half baked in the case that we have
                                    more than one state for a task spec - but I don't think those
                                    are being reported in the list, so it may not matter)
                Any task with a blank or None as the description are excluded from the list (i.e. gateways)


Because the output from this list may be used in a variety of contexts, the implementation is left to the user.

MultiInstance Notes
-------------------

**loopCardinality** - This variable can be a text representation of a
number - for example '2' or it can be the name of a variable in
task.data that resolves to a text representation of a number.
It can also be a collection such as a list or a dictionary. In the
case that it is a list, the loop cardinality is equal to the length of
the list and in the case of a dictionary, it is equal to the list of
the keys of the dictionary.

If loopCardinality is left blank and the Collection is defined, or if
loopCardinality and Collection are the same collection, then the
MultiInstance will loop over the collection and update each element of
that collection with the new information. In this case, it is assumed
that the incoming collection is a dictionary, currently behavior for
working with a list in this manner is not defined and will raise an error.

**Collection** This is the name of the collection that is created from
the data generated when the task is run. Examples of this would be
form data that is generated from a UserTask or data that is generated
from a script that is run. Currently the collection is built up to be
a dictionary with a numeric key that corresponds to the place in the
loopCardinality. For example, if we set the loopCardinality to be a
list such as ['a','b','c] the resulting collection would be {1:'result
from a',2:'result from b',3:'result from c'} - and this would be true
even if it is a parallel MultiInstance where it was filled out in a
different order.

**Element Variable** This is the variable name for the current
iteration of the MultiInstance. In the case of the loopCardinality
being just a number, this would be 1,2,3, . . .  If the
loopCardinality variable is mapped to a collection it would be either
the list value from that position, or it would be the value from the
dictionary where the keys are in sorted order.  It is the content of the
element variable that should be updated in the task.data. This content
will then be added to the collection each time the task is completed.

Example:
  In a sequential MultiInstance, loop cardinality is ['a','b','c'] and elementVariable is 'myvar'
  then in the case of a sequential multiinstance the first call would
  have 'myvar':'a' in the first run of the task and 'myvar':'b' in the
  second.

Example:
  In a Parallel MultiInstance, Loop cardinality is a variable that contains
  {'a':'A','b':'B','c':'C'} and elementVariable is 'myvar' - when the multiinstance is ready, there
  will be 3 tasks. If we choose the second task, the task.data will
  contain 'myvar':'B'.

Custom Script Engines
---------------------

You may need to modify the default script engine, whether because you need to make additional
functionality available to it, or because you might want to restrict its capabilities for
security reasons.

.. warning::

   The default script engine does little to no sanitization and uses eval
   and exec!  If you have security concerns, you should definitely investigate
   replacing the default with your own implementation.

The default script engine imports the following objects:

- timedelta
- datetime
- dateparser
- pytz

You could add other standard python modules or any code you've implemented
yourself.

In our example models so far, we've been using DMN tables to obtain product
information.  DMN tables have a **lot** of uses so we wanted to feature them
prominently, but in a simple way.

If a customer was selecting a product, we would surely have information about
how the product could be customized in a database somewhere.  We would not hard
code product information in our diagram (although it is much easier to modify the
BPMN diagram than change the code itself!).

SpiffWorkflow is obviously **not** going to know how to make a call to **your**
database.  However, you can implement the call yourself and make it available as
a method that can be used within a script task.

We are not going to actually include a database and write code for connecting to
and querying it, but we can model the scenario with a simple dictionary lookup
since we only have 7 products.

.. code:: python

    from collections import namedtuple

    from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine

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

    additions = {
        'lookup_product_info': lookup_product_info,
        'lookup_shipping_cost': lookup_shipping_cost
    }

    CustomScriptEngine = PythonScriptEngine(scriptingAdditions=additions)

We pass the script engine we created to the workflow when we load it.

.. code:: python

    return BpmnWorkflow(parser.get_spec(process), script_engine=CustomScriptEngine)

We can use the custom functions in script tasks like any normal function:

.. figure:: figures/custom_script_usage.png
   :scale: 30%
   :align: center

   Workflow with lanes

And we can simplify our 'Call Activity' flows:

.. figure:: figures/call_activity_script_flow.png
   :scale: 30%
   :align: center

   Workflow with lanes

We have also done some work using `Restricted Python <https://restrictedpython.readthedocs.io/en/latest/>`_
to provide more secure alternatives to standard python functions.

Serialization
-------------

So far, we've only considered the context where we will run the workflow from beginning to end in one
setting. This may not always be the case, we may be executing the workflow in the context of a web server where we
may have a user request a web page where we open a specific workflow that we may be in the middle of, do one step of
that workflow and then the user may be back in a few minutes, or maybe a few hours depending on the application.

To accomplish this, we can import the serializer

.. code:: python

    from SpiffWorkflow.bpmn.serializer.BpmnSerializer import BpmnSerializer

We'll give the user the option of dumping the workflow at any time.

.. code:: python

    filename = input('Enter filename: ')
    state = BpmnSerializer().serialize_workflow(workflow, include_spec=True)
    with open(filename, 'w') as dump:
        dump.write(state)

We'll ask them for a filename and use the serializer to dump the state to
that file.

To restore the workflow:

.. code:: python

    if args.restore is not None:
        with open(args.restore) as state:
            wf = BpmnSerializer().deserialize_workflow(state.read(), workflow_spec=None)

This state is just a big JSON string, and in some cases SpiffWorkflow uses a Python construct known as a 'pickle' to
save more complicated data. (go ahead, look at it.  It won't make much sense, but you can get an idea of what it is
doing).

