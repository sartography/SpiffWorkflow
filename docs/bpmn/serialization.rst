Introduction
============

Given the long-running nature of many workflows, robust serialization capabilities are critical to any kind of
workflow execution library.  We face several problems in serializing workflows:

- workflows may contain arbitrary data whose serialization mechanisms cannot be built into the library itself
- workflows may contain custom tasks and these also cannot be built into the library
- workflows may contain hundreds of tasks, generating very large serializations
- objects contained in the workflow data might also be very large
- the serialized data needs to be stored somewhere and there is no one-size-fits-all way of doing this

In the first section of this document, we'll show how to handle the first problem.

:doc:`custom_task_spec` contains an example of handling the second problem.

In the second section of this document, we'll discuss some of the ways the remaining problems might be alleviated
though creative use of the serializer's capabilities.

.. _serializing_custom_objects:

Serializing Custom Objects
==========================

In :doc:`script_engine`, we add some custom methods and objects to our scripting environment.  We create a simple
class (a :code:`namedtuple`) that holds the product information for each product.

We'd like to be able to save and restore our custom object.  This code lives in :app:`spiff/product_info.py`.

.. code:: python

    ProductInfo = namedtuple('ProductInfo', ['color', 'size', 'style', 'price'])

    def product_info_to_dict(obj):
        return {
            'color': obj.color,
            'size': obj.size,
            'style': obj.style,
            'price': obj.price,
        }

    def product_info_from_dict(dct):
        return ProductInfo(**dct)

And in :app:`spiff/custom_object.py`:

.. code-block:: python

    from SpiffWorkflow.spiff.serializer.config import SPIFF_CONFIG
    from ..serializer.file import FileSerializer

    registry = FileSerializer.configure(SPIFF_CONFIG)
    registry.register(ProductInfo, product_info_to_dict, product_info_from_dict)
    serializer = FileSerializer(dirname, registry=registry)

We don't have any custom task specs in this example, so we can use the default serializer configuration for the
module we're using.  We'll use the :app:`spiff/serializer/file/serializer.py` serializer.  This is a very simple
serializer -- it converts the entire workflow to the default JSON format and writes it to disk in a readable
way.

.. note::

    The default :code:`BpmnWorkflowSerializer` has a `serialize_json` method that essentially does the same thing,
    except without formatting the JSON.  We bypass this so we can intercept the JSON-serializable representation
    and write it ourselves to a location of our choosing.

We initialize a :code:`registry` using the serializer; this registry contains the conversions for the objects
used workflow-internally.

Now we can add our custom serialization methods to this registry using the :code:`registry.register` method.  The
arguments here are:

- the class that requires serialization
- a method that creates a dictionary representation of the object
- a method that recreates the object from that representation

Registering an object sets up relationships between the class and the serialization and deserialization methods.

The :code:`register` method assigns a :code:`typename` for the class, and generates partial functions that call the
appropriate methods based on the :code:`typename`, and stores *these* conversion mechanisms.

.. note::

    The supplied :code:`to_dict` and :code:`from_dict` methods must always return and accept dictionaries, even if
    they might have been serialized some other way.

    If you're interested in how this works, the heart of the registry is the
    `DictionaryConverter <https://github.com/sartography/SpiffWorkflow/blob/main/SpiffWorkflow/bpmn/serializer/helpers/dictionary.py>`_.

    The price is a slightly less customizable serialized format; the benefit is that these partial functions can
    replace humongous :code:`if/else` blocks that test for specific classes and attributes.

Optimizing Serializations
=========================

File Serializer
---------------

Now we'll turn to the customizations we made in the :app:`serializer/file/serializer.py`.

We've extended the :code:`BpmnWorkflowSerializer` to take a directory where we'll write our files, and additionally
we'll impose some structure inside this dictionary.  We'll separate serialized workflow specs from instance data, and
set an output format that we can actually read.

Our engine requires a certain API from our serializer, and that's what the remainder of the methods are.  We won't
go into these method here, as they don't *actually* have much to do with the library.  We made few (the
:app:`spiff/custom_object.py`) or no modifications (the :app:`spiff/file.py`) so there isn't much to discuss.

We call `self.to_dict` and `self.from_dict`, which handle all conversions based on how we've set up the 
:code:`registry`.

.. note::

    We haven't referenced any particular code, as almost all the code here is about managing our directory
    structure and formatting the JSON output appropriately.

The file serializer is actually *not* particularly optimized, but it is simple to understand, while also providing
the evidence that you probably want to do more.  The output here is essentially the what you get by default.  This
useful to be able to easily see in and of itself, and if you examine it, you'll see there would be a lot of
opportunity for splitting the output into its components and handling them separately.

SQLite Serializer
-----------------

We have a second example serializer that stores serializations in a SQLite database in
:app:`serializer/sqlite/serializer.py`.  This might be a slightly more realistic use case of what you want to do,
so we'll discuss this in a little more detail (but it is also a considerably more complex example).

Our database schema actually takes care of much of the work, but since this isn't an SQL tutorial, I'll just refer you
to the file that contains it: :app:`serializer/sqlite/schema.sql`.  Of course, you do not have to interact with the
database directly (or even use a database at all) and some of all of the triggers and views and so forth could be
replaced with Python code (or simplified quite a bit if using a more robust DB).

This is intended to be a somewhat extreme example in order to make it clear that you really aren't bound to
retrieving and storing a gigantic blob, and the logic for dealing with it does not have to be interspersed with the
rest of your code.

In addition to our triggers, we also rely pretty heavily on SQLite adapters.  Between these two things, we hardly
have to worry about the types of objects we get back at all!

From our :code:`execute` method:

.. code-block:: python

    conn = sqlite3.connect(self.dbname, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    conn.execute("pragma foreign_keys=on")
    sqlite3.register_adapter(UUID, lambda v: str(v))
    sqlite3.register_converter("uuid", lambda s: UUID(s.decode('utf-8')))
    sqlite3.register_adapter(dict, lambda v: json.dumps(v))
    sqlite3.register_converter("json", lambda s: json.loads(s))

We use :code:`UUID` for spec and instance IDs and store all our workflow data as JSON.  Our serializer guarantees
that its output will be JSON-serializable, so when we store it, we can just drop its output right into the DB, and
feed the DB output back into the serializer.

To help this process along, we've customized a few of the default conversions for our specs.

.. code-block:: python

    class WorkflowConverter(BpmnWorkflowConverter):

        def to_dict(self, workflow):
            dct = super(BpmnWorkflowConverter, self).to_dict(workflow)
            dct['bpmn_events'] = self.registry.convert(workflow.bpmn_events)
            dct['subprocesses'] = {}
            dct['tasks'] = list(dct['tasks'].values())
            return dct

    class SubworkflowConverter(BpmnSubWorkflowConverter):

        def to_dict(self, workflow):
            dct = super().to_dict(workflow)
            dct['tasks'] = list(dct['tasks'].values())
            return dct

    class WorkflowSpecConverter(BpmnProcessSpecConverter):

        def to_dict(self, spec):
            dct = super().to_dict(spec)
            dct['task_specs'] = list(dct['task_specs'].values())
            return dct

We aren't making extensive customizations here, mainly just switching some dictionaries to lists; this is because we
store these items in separate tables, so it's convenient to get an output that can be passed directly to an
:code:`insert` statement.

When we configure our engine, we update the serializer configuration to use these classes (this code is from
:app:`spiff/sqlite.py`:

.. code-block:: python

    from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG
    from ..serializer.sqlite import (
        SqliteSerializer,
        WorkflowConverter,
        SubworkflowConverter,
        WorkflowSpecConverter
    )

    DEFAULT_CONFIG[BpmnWorkflow] = WorkflowConverter
    DEFAULT_CONFIG[BpmnSubWorkflow] = SubworkflowConverter
    DEFAULT_CONFIG[BpmnProcessSpec] = WorkflowSpecConverter

    dbname = 'spiff.db'

    with sqlite3.connect(dbname) as db:
        SqliteSerializer.initialize(db)

    registry = SqliteSerializer.configure(DEFAULT_CONFIG)
    serializer = SqliteSerializer(dbname, registry=registry)

Finally, let's look at two of the methods we've implemented for the API required by our engine:

.. code-block:: python

    def _create_workflow(self, cursor, workflow, spec_id):
        dct = super().to_dict(workflow)
        wf_id = uuid4()
        stmt = "insert into workflow (id, workflow_spec_id, serialization) values (?, ?, ?)"
        cursor.execute(stmt, (wf_id, spec_id, dct))
        if len(workflow.subprocesses) > 0:
            cursor.execute("select serialization->>'name', descendant from spec_dependency where root=?", (spec_id, ))
            dependencies = dict((name, id) for name, id in cursor)
            for sp_id, sp in workflow.subprocesses.items():
                cursor.execute(stmt, (sp_id, dependencies[sp.spec.name], self.to_dict(sp)))
        return wf_id

    def _get_workflow(self, cursor, wf_id, include_dependencies):
        cursor.execute("select workflow_spec_id, serialization as 'serialization [json]' from workflow where id=?", (wf_id, ))
        row = cursor.fetchone()
        spec_id, workflow = row[0], self.from_dict(row[1])
        if include_dependencies:
            workflow.subprocess_specs = self._get_subprocess_specs(cursor, spec_id)
            cursor.execute(
                "select descendant as 'id [uuid]', serialization as 'serialization [json]' from workflow_dependency where root=? order by depth",
                (wf_id, )
            )
            for sp_id, sp in cursor:
                task = workflow.get_task_from_id(sp_id)
                workflow.subprocesses[sp_id] = self.from_dict(sp, task=task, top_workflow=workflow)
        return workflow

We store subprocesses in the same table as top level processes because they are essentially the same thing.
We maintain a table that stores the parent/child relationships in a separate spec dependency table.  While we don't do
this currently, we could modify our queries to ignore subprocesses that have been completed when we retrieve a workflow:
they could potentially contain many tasks that will never be revisited.  Or, conversely, we could limit what we restore
to subprocesses that had :code:`READY` tasks to avoid loading something that is waiting for a timer that will fire in
two weeks.

We did not show the code for serializing workflow specs, but it is similar -- all specs, whether top-level or for
subprocesses and call activities live in one table, with a second that keeps track of dependencies between them.  This
would make it possible to wait to load a spec until the task it was associated with needed to be executed.

We also maintain task data separately from information about workflow state; so while we're not doing this now, it provides
the potential to selectively retrieve it -- for example, it could be omitted from :code:`COMPLETED` tasks.

What I aim to get across here is that there are quite a few possiblities for customizing how your application serializes
its workflows -- you're not limited to a giant JSON blob that you get by default.


Serialization Versions
======================

As we make changes to Spiff, we may change the serialization format.  For example, in 1.2.1, we changed
how subprocesses were handled interally in BPMN workflows and updated how they are serialized and we upraded the
serializer version to 1.1.

Since workflows can contain arbitrary data, and even SpiffWorkflow's internal classes are designed to be customized in ways
that might require special serialization and deserialization, it is possible to override the default version number, to
provide users with a way of tracking their own changes.

If you have not provided a custom version number, SpiffWorkflow will attempt to migrate your workflows from one version
to the next if they were serialized in an earlier format.

If you've overridden the serializer version, you may need to incorporate our serialization changes with
your own.  You can find our migrations in
`SpiffWorkflow/bpmn/serilaizer/migrations <https://github.com/sartography/SpiffWorkflow/tree/main/SpiffWorkflow/bpmn/serializer/migration>`_

These are broken up into functions that handle each individual change, which will hopefully make it easier to incoporate them
into your upgrade process, and also provides some documentation on what has changed.
