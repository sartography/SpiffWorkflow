SpiffWorkflow Exceptions
========================

Details about the exceptions and exception hierarchy within SpiffWorkflow

SpiffWorkflowException
----------------------
Base exception for all exceptions raised by SpiffWorkflow

ValidationException
-------------------

**Extends**
SpiffWorkflowException

Thrown during the parsing of a workflow.

**Attributes/Methods**

- **tag**:  The type of xml tag being parsed
- **id**:  the id attribute of the xml tag, if available.
- **name**:  the name attribute of the xml tag, if available.
- **line_number**:  the line number where the tag occurs.
- **file_name**: The name of the file where the error occurred.
- **message**:  a human readable error message.


WorkflowException
-----------------
When an error occurs with a Task Specification (maybe should have been called
a SpecException)

**Extends**
SpiffWorkflowException

**Attributes/Methods**

- **task_spec**:  The TaskSpec - the specific Task, Gateway, etc... that caused the error to happen.
- **error**:  a human readable error message describing the problem.


WorkflowDataException
---------------------
When an exception occurs moving data between tasks and Data Objects (including
data inputs and data outputs.)

**Extends**
WorkflowException

**Attributes/Methods**

(in addition to the values in a WorkflowException)

 - **task**:  The specific task (not the task spec, but the actual executing task)
 - **data_input**: The spec of the input variable
 - **data_output**: The spec of the output variable

WorkflowTaskException
---------------------
**Extends**
WorkflowException

It will accept the line_number and error_line as arguments - if the
underlying error provided is a SyntaxError it will try to derive this
information from the error.
If this is a name error, it will attempt to calculate a did-you-mean
error_msg.

**Attributes/Methods**

(in addition to the values in a WorkflowException)

 - **task**:  The specific task (not the task spec, but the actual executing task)
 - **error_msg**: The detailed human readable message.  (conflicts with error above)
 - **exception**: The original exception this wraps around.
 - **line_number** The line number that contains the error
 - **offset** The point in the line that caused the error
 - **error_line** The content of the line that caused the error.
 - **get_task_trace**:  Provided a specific Task, will work it's way through the workflow/sub-processes and 
   call activities to show where an error occurred.  Useful if the error happened within a deeply nested 
   structure (where call activities include call activities ....)
 - **did_you_mean_name_error**: Compares a missing data value with the contents of the data

