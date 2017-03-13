Tutorial
========

Introduction
------------

In this chapter we are going to use Spiff Workflow to solve a real-world
problem: We will create a workflow for triggering a nuclear strike.

We are assuming that you are familiar with the :ref:`intro`.

Assume you want to send the rockets, but only after both the president and
a general have signed off on it.

Implementing the tasks
----------------------

The first step is to create a :class:`SpiffWorkflow.specs.TaskSpec` that
fires the rocket::

    from SpiffWorkflow.specs import Simple

    class NuclearStrike(Simple):
        def _on_complete_hook(self, my_task):
            print("Rocket sent!")

Save this file as ``strike.py``.

Now we are ready to define the workflow. There are two different
ways of doing this: Either by deserializing (from XML or JSON), or using
Python.
In order to use XML or JSON, you will have to also extend the serializer for
the NuclearStrike first. We don't want to do that yet, so we are using Python
instead.

Creating the workflow specification (using Python)
--------------------------------------------------

In Python, the workflow is defined as follows:

.. literalinclude:: nuclear.py

Hopefully the code is self explaining.
Using Python to write a workflow can quickly become tedious. It is
usually a better idea to use another format.

Preparing a serializer
----------------------

Before we can use JSON to specify a workflow, we first need to teach
SpiffWorkflow how our custom `NuclearChoice` looks in JSON. So the first
step is to create a serializer. We also implement the deserializer for
demonstration, though it is not needed to complete this tutorial:

.. literalinclude:: serialize.py

We save the serializer as ``serialize.py``.
We also need to update ``strike.py`` as follows:

.. literalinclude:: strike.py

You are now ready to create the specification from JSON.

Creating a workflow specification (using JSON)
----------------------------------------------

Once you have completed the serializer as shown above, you can
write the specification in JSON.

Here is an example that is doing exactly the same as the Python
WorkflowSpec above:

.. literalinclude:: nuclear.json

Creating a workflow out of the specification
--------------------------------------------

Now it is time to get started and actually create and execute
a workflow according to the specification.

Since we included *manual* tasks in the specification, you will want
to implement a user interface in practice, but we are just going to
assume that all tasks are automatic for this tutorial:

.. literalinclude:: start.py

Serializing a workflow
----------------------

If you want to store a WorkflowSpec, you can use this::

    import json
    from serializer import NuclearSerializer
    from nuclear import NuclearStrikeWorkflowSpec

    serializer = NuclearSerializer()
    spec = NuclearStrikeWorkflowSpec()
    data = serializer.serialize_workflow_spec(spec)
    json_obj = json.loads(data)
    pretty = json.dumps(json_obj, indent=4, separators=(',', ': '))
    open('pretty.json', 'w').write(pretty)

If you want to store a workflow instance, you can use this::

    from serializer import NuclearSerializer
    from nuclear import NuclearStrikeWorkflowSpec

    serializer = NuclearSerializer()
    spec = NuclearStrikeWorkflowSpec()
    workflow = Workflow(spec)
    data = serializer.serialize_workflow(workflow)
    json_obj = json.loads(data)
    pretty = json.dumps(json_obj, indent=4, separators=(',', ': '))
    open('pretty.json', 'w').write(pretty)
