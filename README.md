Spiff Workflow
==============
Spiff Workflow is a library implementing a framework for workflows.
It is based on http://www.workflowpatterns.com and implemented in pure Python.


Supported Workflow Patterns
----------------------------
Hint: The examples are located in tests/data/spiff/.

  Control-Flow Patterns:

     1. Sequence [control-flow/sequence.xml]
     2. Parallel Split [control-flow/parallel_split.xml]
     3. Synchronization [control-flow/synchronization.xml]
     4. Exclusive Choice [control-flow/exclusive_choice.xml]
     5. Simple Merge [control-flow/simple_merge.xml]
     6. Multi-Choice [control-flow/multi_choice.xml]
     7. Structured Synchronizing Merge [control-flow/structured_synchronizing_merge.xml]
     8. Multi-Merge [control-flow/multi_merge.xml]
     9. Structured Discriminator [control-flow/structured_discriminator.xml]
    10. Arbitrary Cycles [control-flow/arbitrary_cycles.xml]
    11. Implicit Termination [control-flow/implicit_termination.xml]
    12. Multiple Instances without Synchronization [control-flow/multi_instance_without_synch.xml]
    13. Multiple Instances with a Priori Design-Time Knowledge [control-flow/multi_instance_with_a_priori_design_time_knowledge.xml]
    14. Multiple Instances with a Priori Run-Time Knowledge [control-flow/multi_instance_with_a_priori_run_time_knowledge.xml]
    15. Multiple Instances without a Priori Run-Time Knowledge [control-flow/multi_instance_without_a_priori.xml]
    16. Deferred Choice [control-flow/deferred_choice.xml]
    17. Interleaved Parallel Routing [control-flow/interleaved_parallel_routing.xml]
    18. Milestone [control-flow/milestone.xml]
    19. Cancel Task [control-flow/cancel_task.xml]
    20. Cancel Case [control-flow/cancel_case.xml]

    22. Recursion [control-flow/recursion.xml]
    23. Transient Trigger [control-flow/transient_trigger.xml]
    24. Persistent Trigger [control-flow/persistent_trigger.xml]
    25. Cancel Region [control-flow/cancel_region.xml]
    26. Cancel Multiple Instance Task [control-flow/cancel_multi_instance_task.xml]
    27. Complete Multiple Instance Task [control-flow/complete_multiple_instance_activity.xml]
    28. Blocking Discriminator [control-flow/blocking_discriminator.xml]
    29. Cancelling Discriminator [control-flow/cancelling_discriminator.xml]
    30. Structured Partial Join [control-flow/structured_partial_join.xml]
    31. Blocking Partial Join [control-flow/blocking_partial_join.xml]
    32. Cancelling Partial Join [control-flow/cancelling_partial_join.xml]
    33. Generalized AND-Join [control-flow/generalized_and_join.xml]
    34. Static Partial Join for Multiple Instances [control-flow/static_partial_join_for_multi_instance.xml]
    35. Cancelling Partial Join for Multiple Instances [control-flow/cancelling_partial_join_for_multi_instance.xml]
    36. Dynamic Partial Join for Multiple Instances [control-flow/dynamic_partial_join_for_multi_instance.xml]
    37. Acyclic Synchronizing Merge [control-flow/acyclic_synchronizing_merge.xml]
    38. General Synchronizing Merge [control-flow/general_synchronizing_merge.xml]
    39. Critical Section [control-flow/critical_section.xml]
    40. Interleaved Routing [control-flow/interleaved_routing.xml]
    41. Thread Merge [control-flow/thread_merge.xml]
    42. Thread Split [control-flow/thread_split.xml]
    43. Explicit Termination [control-flow/explicit_termination.xml]

  Workflow Data Patterns:

     1. Task Data [data/task_data.xml]
     2. Block Data [data/block_data.xml]
     9. Task to Task [data/task_to_task.xml]
    10. Block Task to Sub-Workflow Decomposition [data/block_to_subworkflow.xml]
    11. Sub-Workflow Decomposition to Block Task [data/subworkflow_to_block.xml]

  Specs that have no corresponding workflow pattern on workflowpatterns.com:

    Execute - spawns a subprocess and waits for the results
    Transform - executes commands that can be used for data transforms
    Celery - executes a Celery task (see http://celeryproject.org/)


Contact
--------
Mailing List: http://groups.google.com/group/spiff-devel/


Usage
------
API documentation is embedded into the Spiff Workflow source code and
currently not yet available elsewhere. Other developer documentation has not
yet been written.

If you need more help, please drop by our mailing list. You might actually
make someone write the missing pieces of documentation.

```
from SpiffWorkflow.specs import *
from SpiffWorkflow import Workflow

spec = WorkflowSpec()
wf   = Workflow(spec)
...
```


How it works
------------

### Functionality

One critical concept to know about SpiffWorkflow that helps with understanding
the code is the difference between a `TaskSpec `and `Task` and the difference
between a `WorkflowSpec` and `Workflow`.

A WorkflowSpec and TaskSpec are used to define your workflow. All types of
tasks (Join, Split, Execute, Wait, etc) are derived from TaskSpec. The Specs
can be deserialized from known formats like OpenWFE. You build your
WorkflowSpec by chaining TaskSpecs together in a tree.

When you want to actually run the process, you create a Workflow instance
from the WorkflowSpec (pass the spec to the Workflow initializer).

How this works from there is based on the principles of computer programming
(remember, this project comes from the academic world). A `derivation tree` is
created based off of the spec using a hierarchy of Task objects (not TaskSpecs,
but each Task points to the TaskSpec that generated it).
For more documentation of the derivation tree have a look at the
[SpiffWorkflow wiki](https://github.com/knipknap/SpiffWorkflow/wiki).

Think of a derivation tree as tree of execution paths (some, but not all, of
which will end up executing). Each Task object is basically a node in the
derivation tree. Each task in the tree links back to its parent (there are no
connection objects). The processing is done by walking down the derivation
tree one Task at a time and moving the task (and it's children) through the
sequence of states towards completion. The states are documented in
[Task.py](https://github.com/knipknap/SpiffWorkflow/blob/master/SpiffWorkflow/Task.py|the code).

The Workflow and Task classes are in the root of the project. All the specs
(TaskSpec, WorkflowSpec, and all derived classes) are in the specs
subdirectory.

You can serialize/deserialize specs and open standards like OpenWFE are
supported (and others can be coded in easily). You can also
serialize/deserialize a running workflow (it will pull in its spec as
well).

Another important distinction is between properties and attributes.
Properties belong to TaskSpecs. They are static at run-time and belong
to the design of the workflow. Attributes are dynamic and assigned to
Tasks (nodes in the execution path).

There's a decent eventing model that allows you to tie in to and receive
events (for each task, you can get event notifications from its TaskSpec).
The events correspond with how the processing is going in the derivation
tree, not necessarily how the workflow as a whole is moving. See
[TaskSpec.py](https://github.com/knipknap/SpiffWorkflow/blob/master/SpiffWorkflow/specs/TaskSpec.py)
for docs on events.

### Understanding FUTURE, WAITING, READY, and COMPLETE states

 * FUTURE means the processor has predicted that this this path will be taken and this task will definitely run.
 * If a task is waiting on predecessors to run then it is in FUTURE state (not WAITING).
 * READY means "preconditions are met for marking this task as complete".
 * You can try to complete a task at any point. If it is in FUTURE state and does not complete, it can fall back to READY state.


*WAITING* can be confusing:

 * WAITING means "I am in the process of doing my work and have not finished.
   When the work is finished, then I will be READY for completion and will go
   to READY state."
 * WAITING always comes after FUTURE and before READY. 
 * WAITING is an optional state.


*REACHED* may also be confusing unless you remember that it means that the
processor has now _reached_ this task in the execution path:

 * REACHED means processing has reached this task in the derivation tree.
 This is not a state, but an event.
 * A task is always reached before it becomes READY.

You can nest workflows (using the SubWorkflowSpec).

The serialization code is done well which makes it easy to add new formats
if we need to support them.

To understand better how a TaskSpec pattern works, look at [the workflow
patterns](http://www.workflowpatterns.com) web site; especially the flash
animations showing how each type of task works.

The tasks labelled "ThreadXXXX" create logical threads based on the model
in http://www.workflowpatterns.com. There is no python threading implemented.
However, there is some locking and mutex code in place.

### State Transitions

![state-diagram.png](https://github.com/knipknap/SpiffWorkflow/raw/master/doc/figures/state-diagram.png)
