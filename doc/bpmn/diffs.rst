Diff Utilities
==============

.. note::

    This is a brand new feature so it may change.

It is possible to generate comparisions between two BPMN specs and also to compare an existing workflow instance
against a spec diff to provide information about whether the spec can be updated for the instance.

Individual diffs provide information about a single spec or workflow and spec.  There are also two helper functiond
for calculating diffs of dependencies for a top level spec or workflow and its subprocesses, and a workflow migration
function.

Creating a diff requires a serializer :code:`registry` (see :ref:`serializing_custom_objects` for more information
about this).  The serializer already needs to know about all the attributes of each task spec; it also knows how to
create dictionary representations of the objects.  Therefore, we can serialize an object and just compare the output to
figure which attributes have changed.

Let's add some of the specs we used earlier in this tutorial:

.. code-block:: console

    ./runner.py -e spiff_example.spiff.diffs add -p order_product \
        -b bpmn/tutorial/task_types.bpmn \
        -d bpmn/tutorial/product_prices.dmn

    ./runner.py -e spiff_example.spiff.diffs add -p order_product \
        -b bpmn/tutorial/gateway_types.bpmn \
        -d bpmn/tutorial/{product_prices,shipping_costs}.dmn

    ./runner.py -e spiff_example.spiff.diffs add -p order_product \
        -b bpmn/tutorial/{top_level,call_activity}.bpmn \
        -d bpmn/tutorial/{shipping_costs,product_prices}.dmn

    ./runner.py -e spiff_example.spiff.diffs add -p order_product \
        -b bpmn/tutorial/{top_level_script,call_activity_script}.bpmn \
        -d bpmn/tutorial/shipping_costs.dmn

The IDs of the specs we've added can be obtained with:

.. code-block:: console

    ./runner.py -e spiff_example.spiff.diffs list_specs

    09400c6b-5e42-499d-964a-1e9fe9673e51  order_product        bpmn/tutorial/top_level.bpmn
    9da66c67-863f-4b88-96f0-76e76febccd0  order_product        bpmn/tutorial/gateway_types.bpmn
    e0d11baa-c5c8-43bd-bf07-fe4dece39a07  order_product        bpmn/tutorial/task_types.bpmn
    f679a7ca-298a-4bff-8b2f-6101948715a9  order_product        bpmn/tutorial/top_level_script.bpmn


Model Diffs
-----------

First we'll compare :bpmn:`task_types.bpmn` and :bpmn:`gateway_types.bpmn`.  The first diagram is very basic,
containing only one of each task type; the second diagram introduces gateways.  Therefore the inputs and outputs of
several tasks have changed and a number of new tasks were added.

.. code-block: console

    ./runner.py -e spiff_example.spiff.diffs diff_spec -o e0d11baa-c5c8-43bd-bf07-fe4dece39a07 -n 9da66c67-863f-4b88-96f0-76e76febccd0

Those diagrams don't have dependencies, but :bpmn:`top_level.bpmn` and :bpmn:`top_level_script.bpmn` do have
dependencies (:bpmn:`call_activity.bpmn` and :bpmn:`call_activity_script.bpmn`).  See
:ref:`custom_classes_and_functions` for a description of the changes.  Adding the :code:`-d` will include
any dependencies in the diff output.

.. code-block:: console

    ./runner.py -e spiff_example.spiff.diffs diff_spec -d
        -o 09400c6b-5e42-499d-964a-1e9fe9673e51 \
        -n f679a7ca-298a-4bff-8b2f-6101948715a9

We pass the spec ids into our engine, which deserializes the specs and creates a :code:`SpecDiff` to return (see
:app:`engine/engine.py`.

.. code-block:: python

    def diff_spec(self, original_id, new_id):
        original, _ = self.serializer.get_workflow_spec(original_id, include_dependencies=False)
        new, _ = self.serializer.get_workflow_spec(new_id, include_dependencies=False)
        return SpecDiff(self.serializer.registry, original, new)

    def diff_dependencies(self, original_id, new_id):
        _, original = self.serializer.get_workflow_spec(original_id, include_dependencies=True)
        _, new = self.serializer.get_workflow_spec(new_id, include_dependencies=True)
        return diff_dependencies(self.serializer.registry, original, new)

The :code:`SpecDiff` object provides

- a list of task specs that have been added in the new version
- a mapping of original task spec to a summary of changes in the new version
- an alignment of task spec from the original workflow to the task spec in the new version

The code for displaying the output of a single spec diff is in :app:`cli/diff_result.py`.  I will not go into
detail about how it works here since the bulk of it is just formatting.

The libary also has a helper function `diff_dependencies`, which takes two dictionaries of subworkflow specs
(the output of :code:`get_subprocess_specs` method of the parser can also be used directly here).  This method
returns a mapping of name -> :code:`SpecDiff` for each dependent workflow that could be matched by name and a list
of the names of specs in the new version that did not exist in the old.

Instance Diffs
--------------

Suppose we save one instance of our simplest model without completing any tasks and another instance where we
proceed until our order is displayed before saving.  We can list our instances with this command:

.. code-block:: console

    ./runner.py -e spiff_example.spiff.diffs list_instances

    4af0e043-6fd6-448d-85eb-d4e86067433e  order_product        2024-07-02 17:46:57 2024-07-02 17:47:00 
    af180ef6-0437-41fe-b745-8ec4084f3c57  order_product        2024-07-02 17:47:05 2024-07-02 17:47:30

If we diff each of these instances against the version in which we've added gateways, we'll see a list of
tasks whose specs have changed and their states.

.. code-block:: console

    ./runner.py -e spiff_example.spiff.diffs diff_workflow \
        -s 9da66c67-863f-4b88-96f0-76e76febccd0 \
        -w 4af0e043-6fd6-448d-85eb-d4e86067433e

We'll pass these IDs to our engine, which will return a :code:`WorkflowDiff` of the top level workflow and
a dictionary of subprocess id -> :code:`WorkflowDiff` for any existing subprocesses.

.. code-block:: python

    def diff_workflow(self, wf_id, spec_id):
        wf = self.serializer.get_workflow(wf_id)
        spec, deps = self.serializer.get_workflow_spec(spec_id)
        return diff_workflow(self.serializer.registry, wf, spec, deps)

We can retrieve the current spec and its dependencies from the instantiated workflow, so we only need to pass in
the newer version of the spec and its dependencies.

The :code:`WorkflowDiff` object provides

- a list of tasks whose specs have been removed from the new spec
- a list of tasks whose specs have been updated in the new spec
- a mapping of task -> new task spec for each task where an alignment exists in the spec diff

Code for displaying the results is in :app:`cli/diff_result.py`.

If you start an instance of the first version with a subprocess and stop after customizing a product, and
compare it with the second, you'll see completed tasks from the subprocess in the workflow diff output.

Migration Example
-----------------

In some cases, it may be possible to migrate an existing workflow to a new spec.  This is actually quite
simple to accomplish:

.. code-block:: python

    def migrate_workflow(self, wf_id, spec_id, validate=True):

        wf = self.serializer.get_workflow(wf_id)
        spec, deps = self.serializer.get_workflow_spec(spec_id)
        wf_diff, sp_diffs = diff_workflow(self.serializer.registry, wf, spec, deps)

        if validate and not self.can_migrate(wf_diff, sp_diffs):
            raise Exception('Workflow is not safe to migrate!')

        migrate_workflow(wf_diff, wf, spec)
        for sp_id, sp in wf.subprocesses.items():
            migrate_workflow(sp_diffs[sp_id], sp, deps.get(sp.spec.name))
        wf.subprocess_specs = deps

        self.serializer.delete_workflow(wf_id)
        return self.serializer.create_workflow(wf, spec_id)

The :code:`migrate_workflow` function updates the task specs of the workflow based on the alignment in the
diff and sets the spec.  We have to do this for the top level workflow as well as any subwokflows that have
been created.  We also update the dependencies on the top level workflow (subworkflows do not have dependencies).

This function has an optional :code:`reset_mask` argument that can be used to override the default mask of
:code:`TaskState.READY|TaskState.WAITING`.  The children of matching tasks will be dropped and recreated based
on the new spec so that structural changes will be reflected in future tasks.

In this application we delete the old workflow and reserialize with the new, but that's an application
based decision and it would be possible to save both.

We can migrate the version that we did not advance with the following command:

.. code-block:: console

    ./runner.py -e spiff_example.spiff.diffs migrate \
        -s 9da66c67-863f-4b88-96f0-76e76febccd0 \
        -w 4af0e043-6fd6-448d-85eb-d4e86067433e

Deciding whether to migrate is the hard part.  We use a simple algorithm in this application: if any tasks with
specs that have been changed or removed have completed or started running, or any subprocesses have changed, we
assume the workflow cannot be migrated.

.. code-block:: python

    def can_migrate(self, wf_diff, sp_diffs):

        def safe(result):
            mask = TaskState.COMPLETED|TaskState.STARTED
            tasks = result.changed + result.removed
            return len(filter_tasks(tasks, state=mask)) == 0

        for diff in sp_diffs.values():
            if diff is None or not safe(diff):
                return False
        return safe(wf_diff)

This is fairly restrictive and some workflows might be migrateable even when these conditions apply (for example,
perhaps correcting a typo in completed task shouldn't block future structural changes from being applied).  However,
there isn't really a one-size-fits-all decision to be made.  And it could end up being a massiveeffort to develop a
UI that allows decisions like this to be made, so I haven't done any of that in this application.

The hope is that the `SpecDiff` and `WorkflowDiff` objects can provide the necessary information to make these
decisions.