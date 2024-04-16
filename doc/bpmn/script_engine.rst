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

We've modified our engine configuration to use the restricted environment in :app:`misc/restricted.py`

.. code:: python

    from RestrictedPython import safe_globals
    from SpiffWorkflow.bpmn.script_engine import TaskDataEnvironment

    script_env = TaskDataEnvironment(safe_globals)

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
    two script engines (that is the only difference between the two configurations).  If you've made any
    serializer or parser customizations, this is not likely to be possible.

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

We'll create these "services" along with serialization methods in :app:`spiff/product_info.py` (see
:ref:`serializing_custom_objects` for more information about serialization):

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

We'll then make the "services" available to our scripting environment.

.. code:: python

    script_env = TaskDataEnvironment({
        'datetime': datetime,
        'lookup_product_info': lookup_product_info,
        'lookup_shipping_cost': lookup_shipping_cost,
    })

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

We customize a scripting environment to implement the :code:`call_service` method in :app:`spiff/service_task.py`:

.. code:: python

    class ServiceTaskEnvironment(TaskDataEnvironment):

        def __init__(self):
        super().__init__(({
            'datetime': datetime,
            'product_info_from_dict': product_info_from_dict,
        })

        def call_service(self, operation_name, operation_params, task_data):
            if operation_name == 'lookup_product_info':
                product_info = lookup_product_info(operation_params['product_name']['value'])
                result = product_info_to_dict(product_info)
            elif operation_name == 'lookup_shipping_cost':
                result = lookup_shipping_cost(operation_params['shipping_method']['value'])
            else:
                raise Exception("Unknown Service!")
            return json.dumps(result)

    script_env = ServiceTaskEnvironment()

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


Generating BPMN Events Inside the Scripting Environment
=======================================================

When calling external services, there is course a possibility that a failure could occur, and you might want to be
able to pass that information back into the workflow and define how to handle it there.

In this example, we'll have a service that displays the contents of a file and handles :code:`FileNotFoundError`.  We'll
use the diagram :bpmn:`event_handler.bpmn` and the code in :app:`misc/event_handler.py`.

As in the previous section, we'll use the :code:`ServiceTask` from the :code:`spiff` package, but we'll need to extend
it.  This is where we'll handle errors.

We define the following error in our XML (we can do this in our 
`modeler <https://github.com/sartography/bpmn-js-spiffworkflow>`_):

.. code:: xml

    <bpmn:error id="file_not_found" name="file_not_found" errorCode="1">
      <bpmn:extensionElements>
        <spiffworkflow:variableName>filename</spiffworkflow:variableName>
      </bpmn:extensionElements>
    </bpmn:error>

In our scripting enviroment, we'll implement a "read_file" service.  This will of course raise an exception if the
requested file is missing, but will otherwise return the contents.

.. code:: python

    class ServiceTaskEnvironment(TaskDataEnvironment):

        def call_service(self, operation_name, operation_params, context):
            if operation_name == 'read_file':
                return open(operation_params['filename']).read()
            else:
                raise ValueError('Unknown Service')

And here is the code for our task spec.

.. code:: python

    class EventHandlingServiceTask(ServiceTask):

        def _execute(self, my_task):
            script_engine = my_task.workflow.script_engine
            # The param also has a type, but I don't need it
            params = dict((name, script_engine.evaluate(my_task, p['value'])) for name, p in self.operation_params.items())
            try:
                result = script_engine.call_service(self.operation_name, params, my_task.data)
                my_task.data[self._result_variable(my_task)] = result
                return True
            except FileNotFoundError as exc:
                event_definition = ErrorEventDefinition('file_not_found', code='1')
                event = BpmnEvent(event_definition, payload=params['filename'])
                my_task.workflow.top_workflow.catch(event)
                return False
            except Exception as exc:
                raise WorkflowTaskException('Service Task execution error', task=my_task, exception=exc)

If the file was read successfully, we'll set a variable in our task data with the result (the name of the result variable
is optionally specified in the XML and the :code:`_result_variable` method returns either the specified name or a calculated
name otherwise).  We return :code:`True` because the operation was a success (see :doc:`../concepts` for more information
about state transitions).

We'll catch :code:`FileNotFoundError` and construct an event to send it back to the workflow.  What we generate needs
to match what's in the XML.

.. note::

    If you are building an application, you'll probably need to manage known exceptions in a way that is accesible to
    both your modeler and your execution engine, but here we'll just show how to build the event so that it can be
    caught in the diagram in the task spec.

We have to construct an :code:`EventDefinition` that matches what will be generated from the parsed XML (see
:ref:`events` for a general overview of BPMN event handling).  SpiffWorkflow uses the :code:`EventDefinition` to
determine whether a particular task handles an event.  The BPMN spec allows certain events, including Error Events, to
optionally contain a payload.  In this case, we'll set the payload to be the name of the missing file, which can then be
displayed to the user.

We pass our contructed event to the workflow's :code:`catch` method, which will check to see if there are any tasks
waiting for this event.  Each task has a reference to its workflow, but this task occurs in a subworkflow.  Event
handling is done at the outermost level so we'll use :code:`my_task.workflow.top_workflow` to get access to the top
level.

We'll return :code:`False`, since the operation was not a success; this will prevent task execution on that branch,
but will not halt overall workflow execution.  An unhandled exception, as in the last case, will cause the entire
workflow to halt.

.. note::

    The task spec is not the only place error handling could be implemented.  I kind of like this approach, as the task
    spec defines the behavior for a particular type of task and this is part of that.  It would also be possible to extend
    the :code:`PythonScriptEngine` to handle the errors.  The main reason I didn't do that here is that this example
    application can be made less complex if only a scripting environment is supplied.  The script engine, unlike the script
    enviroment, has access to the task and workflow (via the task), and the same thing could be done there as well.


To load this example:

.. code:: console

    ./runner.py -e spiff_example.misc.event_handler add -p read_file -b bpmn/tutorial/event_handler.bpmn
    ./runner.py -e spiff_example.misc.event_handler

.. note:: 

    When running this example, it will probably useful to change the task filter so that all tasks are visible.  Set
    the state to `ANY_MASK` to see all tasks.

Threaded Service Task
=====================

Suppose that we have some potentially time-consuming tasks and we want to execute them in threads so that we aren't
blocking the entire workflow from executing while it runs (the default behavior). In this section, we'll customize a
scripting enviroment that contains a thread pool.

First let's write a simple "service" that simply waits.

.. code:: python

    def wait(seconds, job_id):
        time.sleep(seconds)
        return f'{job_id} slept {seconds} seconds'

We'll make this "service" available in our environment:

.. code:: python

    class ServiceTaskEnvironment(TaskDataEnvironment):

        def __init__(self):
            super().__init__()
            self.pool = ThreadPoolExecutor(max_workers=10)
            self.futures = {}

        def call_service(self, operation_name, operation_params, context):
            if operation_name == 'wait':
                seconds = randrange(1, 30)
                return self.pool.submit(wait, seconds, operation_params['job_id'])
            else:
                raise ValueError("Unknown Service!")

Our service will return a future, and we'll manage these futures via a custom task spec.  The parent class is the
Service Task of the :code:`spiff` package, which provides us with an :code:`operation_name` and
:code:`operation_parameters`.  Each parameter has a name and a type, but I don't need the type, so I'll just get the
values.  The values are expressions that we evaluate against the task data.  We'll map the future to the task in the script
environment.

.. code:: python

    class ThreadedServiceTask(ServiceTask):

        def _execute(self, my_task):
            script_engine = my_task.workflow.script_engine
            params = dict((name, script_engine.evaluate(my_task, p['value'])) for name, p in self.operation_params.items())
            try:
                future = script_engine.call_service(self.operation_name, params, my_task.data)
                script_engine.environment.futures[future] = my_task
            except Exception as exc:
                raise WorkflowTaskException('Service Task execution error', task=my_task, exception=exc)

Since our :code:`_execute` method returns :code:`None`, our task will transition to a :code:`STARTED` state (see
:doc:`../concepts` for more information about state transitions).  SpiffWorkflow will ignore this task from this point on;
this means our engine has to take over.

We'll extend the :code:`Instance` class (defined in :app:`engine/instance.py`) to also check these futures when waiting
tasks are refreshed.  As jobs complete, we'll call :code:`task.complete` to mark the task :code:`COMPLETED`.  The workflow
will then be able to continue down that branch.

.. code:: python

    class ThreadInstance(Instance):

        def update_completed_futures(self):
            futures = self.workflow.script_engine.environment.futures
            finished = [f for f in futures if f.done()]
            for future in finished:
                task = futures.pop(future)
                result = future.result()
                task.data[task.task_spec._result_variable(task)] = result
                task.complete()

        def run_ready_events(self):
            self.update_completed_futures()
            super().run_ready_events()

.. note::

    In a real application, you would probably want a separate service keeping track of the jobs and checking the
    futures rather than polling in the engine, but that can't be easily set up in this example application.

To load and run thie example (as in the previous example, it is probably a good idea to update the task filter to show all
tasks with the `ANY_MASK` state.

.. code:: console

    ./runner.py -e spiff_example.misc.threaded_service_task add -p threaded_service -b bpmn/tutorial/threaded_service_task.bpmn
    ./runner.py -e spiff_example.misc.threaded_service_task


Executing Scripts in a Subprocess
=================================

In this section, we'll show how you might execute your scripts outside of the workflow execution context.  This ia a little
contrived and there are undoubtedly better ways to accomplish it, but this has the advantage of being very simple.

First we'll create an executable that can take a JSON-serialized context and an expression to evaluate or a script to execute
(see :app:`spiff/subprocess_engine.py`).  This little program simply replicates the behavior of the default
script engine.

We import our custom function here rather than our workflow's engine.  We'll also import the registry used by our serializer;
we need to be able to generate JSON when we write our output, so we might as well reuse what we have.

.. code:: python

    from .custom_exec import (
        lookup_product_info,
        lookup_shipping_cost,
        registry,
    )

This emulates how the default script engine handles evaluation and execution.

.. code:: python

    local_ctx = registry.restore(json.loads(args.context))
    global_ctx = globals()
    global_ctx.update(local_ctx)
    if args.external is not None:
        global_ctx.update(registry.restore(json.loads(args.external)))
    if args.method == 'eval':
        result = eval(args.expr, global_ctx, local_ctx)
    elif args.method == 'exec':
        exec(args.script, global_ctx, local_ctx)
        result = local_ctx
    print(json.dumps(registry.convert(result)))

Then we'll tell our scripting enviroment to use the script rather directly invoke :code:`eval` and :code:`exec`.

.. code:: python

    class SubprocessScriptingEnvironment(BasePythonScriptEngineEnvironment):

        def __init__(self, executable, serializer, **kwargs):
            super().__init__(**kwargs)
            self.executable = executable
            self.serializer = serializer

        def evaluate(self, expression, context, external_context=None):
            output = self.run(['eval', expression], context, external_context)
            return self.parse_output(output)

        def execute(self, script, context, external_context=None):
            output = self.run(['exec', script], context, external_context)
            DeepMerge.merge(context, self.parse_output(output))
            return True

        def run(self, args, context, external_context):
            cmd = ['python', '-m', self.executable] + args + ['-c', json.dumps(registry.convert(context))]
            if external_context is not None:
                cmd.extend(['-x', json.dumps(registry.convert(external_context))])
            return subprocess.run(cmd, capture_output=True)

        def parse_output(self, output):
            if output.stderr:
                raise Exception(output.stderr.decode('utf-8'))
            return registry.restore(json.loads(output.stdout))

    executable = 'spiff_example.spiff.subprocess_engine'
    script_env = SubprocessScriptingEnvironment(executable, serializer)

To load this example:

.. code:: console

    ./runner.py -e spiff_example.spiff.custom_exec add -p order_product \
        -b bpmn/tutorial/{top_level_script,call_activity_script}.bpmn
    ./runner.py -e spiff_example.spiff.custom_exec

