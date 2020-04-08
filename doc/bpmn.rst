.. _bpmn_page:

Business Process Model and Notation (BPMN)
==========================================

Business Process Model and Notation (BPMN) is a standard for business process modeling that
provides a graphical notation for specifying business processes, based on a flowcharting technique.
The objective of BPMN is to support business process management, for both technical users and business users,
by providing a notation that is intuitive to business users, yet able to represent complex
process semantics. The BPMN specification also provides a standard XML serialization format, which
is what Spiff Workflow parses.

A reasonable subset of the BPMN notation is supported, including the following elements:

  1. Call Activity
  2. Start Event
  3. End Event (including interrupting)
  4. User and Manual Tasks
  5. Script Task
  6. Exclusive Gateway
  7. Inclusive Gateway (converging only)
  8. Parallel Gateway
  9. MultiInstance & Variants
  10. Intermediate Catch Events (Timer and Message)
  11. Boundary Events (Timer and Message, interrupting and non-interrupting)

.. figure:: figures/action-management.png
   :alt: Example BPMN Workflow

   Example BPMN Workflow

Please refer to http://www.bpmn.org/ for details on BPMN and to the API documentation for instructions on the
use of the BPMN implementation.

MultiInstance Notes
-------------------

A subset of MultiInstance and Looping Tasks are supported. Notably,
the completion condition is not currently supported. 

The following definitions should prove helpful

**loopCardinality** - This variable can be a text representation of a
number - for example '2' or it can be the name of a variable in
task.data that resolves to a text representatoin of a number.
It can also be a collection such as a list or a dictionary. In the
case that it is a list, the loop cardinality is equal to the length of
the list and in the case of a dictionary, it is equal to the list of
the keys of the dictionary.

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
dictionary where the keys are in sorted order.

Example:
  In a sequential MultiInstance, loop cardinality is ['a','b','c'] and elementVariable is 'myvar'
  then in the case of a sequential multiinstance the first call would
  have 'myvar':'a' in the first run of the task and 'myvar':'b' in the
  second. 

Example:
  In a Parallel MultiInstance, Loop cardinality is a variable that contains
  {'a':'A','b':'B','c':'C'} and elementVariable is 'myvar' - when the multiinstance is ready, there
  will be 3 tasks. If we chooose the second task, the task.data will
  contain 'myvar':'B'

Updating Data
------------

While there may be some MultiInstances that will not result in any
data, most of the time there will be some kind of data generated that
will be collected from the MultiInstance. A good example of this is a
UserTask that has an associated form or a script that will do a lookup
on a variable.

Each time the MultiInstance task generates data, the method
task.update_data(data) should be called where data is the data
generated. The 'data' variable that is passed in is assumed to be a
dictionary. Calling task.update_data(...) will ensure that the
MultiInstance gets the correct data to include in the collection. The
task.data is also updated with the dictionary passed to this method.

Looping Tasks
-------------

A looping task sets the cardinality to 25 which is assumed to be a
sane maximum value. The looping task will add to the collection each
time it is processed assuming data is updated as outlined in the
previous paragraph.

To halt the looping the task.terminate_loop()

Each time task.complete() is called (or
workflow.complete_task_by_id(task.id) ), the task will again present
as READY until either the cardinality is exausted, or
task.terminate_loop() is called.

**Caveats**
-----------

At the current time a sequential MultiInstance behaves more like a
Looping Task than a MultiInstance - A true MultiInstace would actually
create multiple copies of the task in the task tree - currently only
one task is created and it is repeated the number of the
loopCardinality 



