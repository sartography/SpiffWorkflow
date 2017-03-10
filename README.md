# Spiff Workflow

[![Build Status](https://travis-ci.org/knipknap/SpiffWorkflow.svg?branch=master)](https://travis-ci.org/knipknap/SpiffWorkflow)
[![Coverage Status](https://coveralls.io/repos/github/knipknap/SpiffWorkflow/badge.svg?branch=master)](https://coveralls.io/github/knipknap/SpiffWorkflow?branch=master)
[![Code Climate](https://lima.codeclimate.com/github/knipknap/SpiffWorkflow/badges/gpa.svg)](https://lima.codeclimate.com/github/knipknap/SpiffWorkflow)
[![Documentation Status](https://readthedocs.org/projects/spiffworkflow/badge/?version=latest)](http://spiffworkflow.readthedocs.io/en/latest/?badge=latest)

## Summary

Spiff Workflow is a workflow engine implemented in pure Python. It is based
on the excellent work of the
[Workflow Patterns initiative](http://www.workflowpatterns.com/).

## Main design goals

- Spiff Workflow aims to directly support as many of the patterns of
  workflowpatterns.com as possible.
- Spiff Workflow uses unit testing as much as possible.
- Spiff Workflow provides a **clean Python API**.
- Spiff Workflow allows for mapping patterns into workflow elements that
  are **easy to understand for non-technical users** in a workflow GUI editor.
- Spiff Workflow implements the best possible **path prediction** for
  workflows.

Spiff Workflow also provides a parser and workflow emulation
layer that can be used to create executable Spiff Workflow specifications
from Business Process Model and Notation (BPMN) documents.

## Quick Intro

The process of using Spiff Workflow involves the following steps:

1. Write a workflow specification. A specification may be written using
   XML ([example](https://github.com/knipknap/SpiffWorkflow/blob/master/tests/SpiffWorkflow/data/spiff/workflow1.xml)),
   JSON, or
   Python ([example](https://github.com/knipknap/SpiffWorkflow/blob/master/tests/SpiffWorkflow/data/spiff/workflow1.py)).
2. Run the workflow using the Python API. Example code for running the workflow:

```python
from SpiffWorkflow.specs import WorkflowSpec
from SpiffWorkflow.storage import XmlSerializer
from SpiffWorkflow import Workflow

# Load the workflow specification:
with open('my_workflow.xml') as fp:
	serializer = XmlSerializer()
	spec = WorkflowSpec.deserialize(serializer, fp.read())

# Create an instance of the workflow, according to the specification.
wf = Workflow(spec)

# Complete tasks as desired. It is the job of the workflow engine to
# guarantee a consistent state of the workflow.
wf.complete_task_from_id(...)

# Of course, you can also persist the workflow instance:
xml = Workflow.serialize(XmlSerializer, 'workflow_state.xml')
```

## Documentation

Full documentation is here:

  https://github.com/knipknap/SpiffWorkflow/wiki
