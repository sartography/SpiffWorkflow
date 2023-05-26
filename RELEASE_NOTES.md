## What's Changed

We've done a lot of work over the last 8 months to the SpiffWorkflow library as we've developed [SpiffArena](https://www.spiffworkflow.org/), a general purpose workflow managment system built ontop of this library.
This has resulted in just a handful of new features. Our main focus was on making SpiffWorkflow more predictable, easier to use, and internally consistent.

## Breaking Changes from 1.x:
* We heavily refactored the way we handle multi-instance tasks internally.  This will break any serialized workflows that contain multi-instance tasks.

## Features and Improvements

### Task States, Transitions, Hooks, and Execution
Previous to 2.0, SpiffWorklow was a little weird about it's states, performing the actual execution in the on_complete() hook.
This was VERY confusing.
Tasks now have a _run() command separate from state change hooks.
The return value of the _run() command can be true (worked), false (failure) or None (not yet done).
This opens the door for better overall state management at the moment it is most critical (when the task is actually executing).
We also added new task state called "STARTED" that describes when a task was started, but hasn't finished yet, an oddly missing state in previous versions.

* Improvement/execution and serialization cleanup by @essweine in https://github.com/sartography/SpiffWorkflow/pull/289
* Bugfix/execute tasks on ready by @essweine in https://github.com/sartography/SpiffWorkflow/pull/303
* Feature/standardize task execution by @essweine in https://github.com/sartography/SpiffWorkflow/pull/307
* do not execute boundary events in catch by @essweine in https://github.com/sartography/SpiffWorkflow/pull/312
* Feature/new task states by @essweine in https://github.com/sartography/SpiffWorkflow/pull/315

### Improved Events
We refactored the way we handle events, making them more powerful and adaptable.
Timer events are now parsed according to the [ISO 8601 standard](https://en.wikipedia.org/wiki/ISO_8601).
* Feature/multiple event definition by @essweine in https://github.com/sartography/SpiffWorkflow/pull/268
* hacks to handle timer events like regular events by @essweine in https://github.com/sartography/SpiffWorkflow/pull/273
* Feature/improved timer events by @essweine in https://github.com/sartography/SpiffWorkflow/pull/284
* reset boundary events in loops by @essweine in https://github.com/sartography/SpiffWorkflow/pull/294
* Bugfix/execute event gateways on ready by @essweine in https://github.com/sartography/SpiffWorkflow/pull/308

### Improved Muliti-Instance Tasks
We refactored how Multi-instance tasks are handled internally, vastly simplifying their representation during execution and serialization.
No more 'phantom gateways'.
* Feature/multiinstance refactor by @essweine in https://github.com/sartography/SpiffWorkflow/pull/292

### Improved Sub-Processes
SpiffWorkflow did not previously distinguish between a Call Activity and a SubProcess however they handle Data Objects very differently.
A Sub Process is now able to access it's parent data objects, a Call Activity can not.
We also wanted the ability to execute Call Activities independently of the parent process.

* Bugfix/subprocess access to data objects by @essweine in https://github.com/sartography/SpiffWorkflow/pull/296
* start workflow while subprocess is waiting by @essweine in https://github.com/sartography/SpiffWorkflow/pull/302
* use same data objects & references in subprocesses after deserialization by @essweine in https://github.com/sartography/SpiffWorkflow/pull/314

### Improved Data Objects / Data Stores
This work will continue in subsequent releases, but we have added support for Data Stores, and it is possible provide your own implementations.
* Data stores by @jbirddog in https://github.com/sartography/SpiffWorkflow/pull/298
* make data objects available to gateways by @essweine in https://github.com/sartography/SpiffWorkflow/pull/325

### Improved Inclusive Gateways
We added support for Inclusive Gateways.
* Feature/inclusive gateway support by @essweine in https://github.com/sartography/SpiffWorkflow/pull/286

### Pre and Post Script Fixes
We previously supported adding a pre-script or post-script to any task but there were a few lingering bugs that needed fixing.
* parse spiff script extensions in service tasks by @essweine in https://github.com/sartography/SpiffWorkflow/pull/257
* pass script to workflow task exec exception by @essweine in https://github.com/sartography/SpiffWorkflow/pull/258
* update execution order for postscripts by @essweine in https://github.com/sartography/SpiffWorkflow/pull/259

### DMN Improvements
We now support a new hit policy of "COLLECT" which allows you to match on an array of items.  DMN support is still limited, but
we are making headway.  Would love to know if people are using these features.
* Support for the "COLLECT" hit policy. by @danfunk in https://github.com/sartography/SpiffWorkflow/pull/267
* Bugfix/handle dash in dmn by @essweine in https://github.com/sartography/SpiffWorkflow/pull/323

### BPMN Validation
We improved validation of BPMN and DMN Files to catch errors earlier.
* Feature/xml validation by @essweine and @danfunk in https://github.com/sartography/SpiffWorkflow/pull/256

### New Serializer
There are some breaking changes in the new serializer, but it is much faster and more stable.  We do attempt to upgrade
your serialized workflows to the new format, but you will definitely encounter issues if you were using multi-instance tasks.
* update serializer version by @essweine in https://github.com/sartography/SpiffWorkflow/pull/277
* Feature/remove old serializer by @essweine in https://github.com/sartography/SpiffWorkflow/pull/278

### Lightening Fast, Stable Tests
* Fix ResourceWarning: unclosed file BpmnParser.py:60 by @jbirddog in https://github.com/sartography/SpiffWorkflow/pull/270
* Option to run tests in parallel by @jbirddog in https://github.com/sartography/SpiffWorkflow/pull/271

### Better Errors
* Feature/better errors by @danfunk in https://github.com/sartography/SpiffWorkflow/pull/283
* Workflow Data Exceptions were broken in the previous error refactor. … by @danfunk in https://github.com/sartography/SpiffWorkflow/pull/287
* added an exception for task not found w/ @burnettk by @jasquat in https://github.com/sartography/SpiffWorkflow/pull/310
* give us a better error if for some reason a task does not exist by @burnettk in https://github.com/sartography/SpiffWorkflow/pull/311

### Flexible Data Management
* Allow for other PythonScriptEngine environments besides task data by @jbirddog in https://github.com/sartography/SpiffWorkflow/pull/288

### Various Enhancements
Make it easier to reference SpiffWorkflow library classes from your own code.
* Feature/add init to schema by @jasquat in https://github.com/sartography/SpiffWorkflow/pull/260
* cleaning up code smell by @danfunk in https://github.com/sartography/SpiffWorkflow/pull/261
* Feature/cleanup task completion by @essweine in https://github.com/sartography/SpiffWorkflow/pull/263
* disambiguate DMN expressions by @essweine in https://github.com/sartography/SpiffWorkflow/pull/264
* Add in memory bpmn/dmn parser functions by @jbirddog in https://github.com/sartography/SpiffWorkflow/pull/320

### Better Introspection
Added the abilty to ask SpiffWorkflow some useful questions about a specification such as "What call activities does this depend on?",
"What messages does this process send and receive", and "What lanes exist on this workflow specification?"
* Parser Information about messages, correlation keys, and the presence of lanes by @danfunk in https://github.com/sartography/SpiffWorkflow/pull/262
* Called elements by @jbirddog in https://github.com/sartography/SpiffWorkflow/pull/316

### Code Cleanup
* Improvement/task spec attributes by @essweine in https://github.com/sartography/SpiffWorkflow/pull/328
* update license by @essweine in https://github.com/sartography/SpiffWorkflow/pull/324
* Feature/remove unused bpmn attributes and methods by @essweine in https://github.com/sartography/SpiffWorkflow/pull/280
* Improvement/remove camunda from base and misc cleanup by @essweine in https://github.com/sartography/SpiffWorkflow/pull/295
* remove minidom by @essweine in https://github.com/sartography/SpiffWorkflow/pull/300
* Feature/remove loop reset by @essweine in https://github.com/sartography/SpiffWorkflow/pull/305
* Feature/create core test package by @essweine in https://github.com/sartography/SpiffWorkflow/pull/306
* remove celery task and dependency by @essweine in https://github.com/sartography/SpiffWorkflow/pull/322
* remove one deprecated and unused feature by @essweine in https://github.com/sartography/SpiffWorkflow/pull/329
* change the order of tasks when calling get_tasks() by @danfunk in https://github.com/sartography/SpiffWorkflow/pull/319

### Improved Documentation
* Fixes grammar, typos, and spellings by @rachfop in https://github.com/sartography/SpiffWorkflow/pull/291
* Updates for 2.0 release by @essweine in https://github.com/sartography/SpiffWorkflow/pull/330
* Bugfix/non bpmn tutorial by @essweine in https://github.com/sartography/SpiffWorkflow/pull/317

### Bug Fixes
* correct xpath for extensions by @essweine in https://github.com/sartography/SpiffWorkflow/pull/265
* prevent output associations from being removed twice by @essweine in https://github.com/sartography/SpiffWorkflow/pull/275
* fix for workflowspec dump by @subhakarks in https://github.com/sartography/SpiffWorkflow/pull/282
* add checks for len == 0 when copying based on io spec by @essweine in https://github.com/sartography/SpiffWorkflow/pull/297
* Improvement/allow duplicate subprocess names by @essweine in https://github.com/sartography/SpiffWorkflow/pull/321
* Resets to tasks with Boundary Events by @danfunk in https://github.com/sartography/SpiffWorkflow/pull/326
* Sub-workflow tasks should be marked as "Future" when resetting to a task before the sub-process. by @danfunk in https://github.com/sartography/SpiffWorkflow/pull/327

## New Contributors
* @subhakarks made their first contribution in https://github.com/sartography/SpiffWorkflow/pull/282
* @rachfop made their first contribution in https://github.com/sartography/SpiffWorkflow/pull/291

**Full Changelog**: https://github.com/sartography/SpiffWorkflow/compare/v1.2.1...v2.0.0
