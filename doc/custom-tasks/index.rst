Implementing Custom Tasks
=========================

Introduction
------------

In this second tutorial we are going to implementing our own task, and
use serialization and deserialization to store and restore it.

If you haven't already, you should first complete the first
:doc:`../tutorial/index`.
We are also assuming that you are familiar with the :doc:`../basics`.

Implementing the custom task
----------------------------

The first step is to create a :class:`SpiffWorkflow.specs.TaskSpec` that
fires the rocket::

    from SpiffWorkflow.specs import Simple

    class NuclearStrike(Simple):
        def _on_complete_hook(self, my_task):
            print("Rocket sent!")

Save this file as ``strike.py``.

Now, before we are ready to define the workflow using XML or JSON, we will
also have extend the serializer to let SpiffWorkflow know how to represent
your NuclearStrike first.

Preparing a serializer
----------------------

Before we can use JSON to specify a workflow, we first need to teach
SpiffWorkflow how our custom `NuclearChoice` looks in JSON. So the first
step is to extend the :mod:`SpiffWorkflow.serializer.json.JSONSerializer`.

.. literalinclude:: serializer.py

We save the serializer as ``serializer.py``.
We also need to update ``strike.py`` as follows:

We also implement the deserializer:
.. literalinclude:: strike.py

You are now ready to create the specification from JSON.

Creating a workflow specification (using JSON)
----------------------------------------------

Now we can use the NuclearStrike in the workflow specification in JSON.

.. literalinclude:: nuclear.json

Note that this specification references our class `strike.NuclearStrike`;
it is otherwise the same as in our first tutorial.

Using the custom serializer and task
------------------------------------

Here we use our brand new serializer in practice:

.. literalinclude:: start.py
