Internal Details for SpiffWorkflow
==================================

A `derivation tree` is created based off of the spec using a hierarchy of Task objects (not TaskSpecs,
but each Task points to the TaskSpec that generated it).

Think of a derivation tree as tree of execution paths (some, but not all, of which will end up executing). Each Task object is basically a node in the derivation tree. Each task in the tree links back to its parent (there are no connection objects). The processing is done by walking down the derivation tree one Task at a time and moving the task (and it's children) through the sequence of states towards completion.

You can serialize/deserialize specs and open standards like OpenWFE are supported (and others can be coded in easily). You can also serialize/deserialize a running workflow (it will pull in its spec as
well).

There's a decent eventing model that allows you to tie in to and receive events (for each task, you can get event notifications from its TaskSpec). The events correspond with how the processing is going in the derivation tree, not necessarily how the workflow as a whole is moving.
See `TaskSpec.py<https://github.com/knipknap/SpiffWorkflow/blob/master/SpiffWorkflow/specs/TaskSpec.py>` for docs on events.

You can nest workflows (using the SubWorkflowSpec).

The serialization code is done well which makes it easy to add new formats if we need to support them.
