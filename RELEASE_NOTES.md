## What's Changed

Since the last release, we've continued to work on making SpiffWorkflow easier to use and internally consistent as well as
added a few new features to support [SpiffArena](https://www.spiffworkflow.org/).

## Breaking Changes from 2.x:

* We refactored task iteration to allow for greater flexibility in selecting tasks.  Usage of `workflow.get_tasks` has changed.
  See [Filtering Tasks](https://spiffworkflow.readthedocs.io/en/latest/bpmn/workflows.html#filtering-tasks) for documentation.
* We've continued to reorganize files in order to impose more structure on the package.  Imports have changed (but we've added
  `__init__.py` files to make these reorganizations less painful in the future).  See an overview of the package structure at
  [What's in the BPMN Module](https://spiffworkflow.readthedocs.io/en/latest/bpmn/imports.html).
* We've simplified the BPMN serializer. [BPMN Serializer](https://spiffworkflow.readthedocs.io/en/latest/bpmn/serialization.html)

## Features and Improvements

### New BPMN Support

* Added support for Conditional Events.

### New BPMN Extensions

* Added the ability to include a payload on Signal, Error, and Escalation Events.
* Added a category to Data Objects.
* Added the ability to choose whether Pre and Post Scripts attach to a MultiInstance Task or each of the instance Tasks.

### General Library Improvements

* Added `__init__` files to modules.
* `TaskState` now handles name/value conversions for any mask.
* Refactored workflow execution to take advatage of the changes to task iteration.
* Unified spec and data serialization for BPMN workflows, and made the serializer easier to configure.
* Retrieve tasks directly from their IDs rather than traversing the tree.
* Removed some of the extra task specs that had been automatically added to every workflow.
* Added a method for allowing task specs to expose internal data.
* We've continued to remove unused code and unneeded tests.
* We've made the documentation more developer-centric.

### Other Changes

* Deprecated the FEEL engine.
* Removed `Box`.

### Bugfixes

* Multiple BPMN Start Events are handled correctly.
* Full support for the BPMN `executable` attribute.
* Fixed a bug in date calculations in Timer Events.
* Ensured that tasks created by Cycle Timers to inherit data from the parent task.
* Delayed the first cycle of the the Cycle Timer by the cycle duration.
* Fixed some bugs relating to how tasks with boundary events are parsed.
* Removed dependencies on descendant tasks from parallel gateway merges that could cause workflow execution to stall.
* Ensured that all dependencies of a subprocess are identified by the BPMN parser.

**Full Changelog**: https://github.com/sartography/SpiffWorkflow/compare/v2.0.1...v3.0.0rc0
