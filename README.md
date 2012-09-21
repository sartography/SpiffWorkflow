Spiff Workflow
==============
Spiff Workflow is a library implementing a framework for workflows.
It is based on http://www.workflowpatterns.com and implemented in pure Python.

In addition, Spiff Workflow provides a parser and workflow emulation
layer that can be used to create executable Spiff Workflow specifications
from Business Process Model and Notation (BPMN) documents.

For documentation please refer to:

  https://github.com/knipknap/SpiffWorkflow/wiki


Contact
-------
Mailing List: http://groups.google.com/group/spiff-devel/

Business Process Model and Notation (BPMN)
------------------------------------------

TODO: move this to the wiki:

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
  7. Parallel Gateway
  8. Intermediate Catch Events (Timer and Message)
  9. Boundary Events (Timer and Message, interrupting and non-interrupting)

The following is an example of a BPMN workflow:

![action-management.png](https://github.com/matthewhampton/SpiffWorkflow/raw/samuel_review_fixes/doc/figures/action-management.png)
