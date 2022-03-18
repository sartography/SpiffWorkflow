## SpiffWorkflow
Spiff Workflow is a workflow engine implemented in pure Python. It is based on
the excellent work of the Workflow Patterns initiative. In 2020 and 2021,
extensive support was added for BPMN / DMN processing.

## Motivation
We created SpiffWorkflow to support the development of low-code business
applications in Python.  Using BPMN will allow non-developers to describe
complex workflow processes in a visual diagram, coupled with a powerful python
script engine that works seamlessly within the diagrams.  SpiffWorkflow can parse
these diagrams and execute them.  The ability for businesses to create
clear, coherent diagrams that drive an application has far reaching potential.
While multiple tools exist for doing this in Java, we believe that wide
adoption of the Python Language, and it's ease of use, create a winning
strategy for building Low-Code applications.


## Build status
[![Build Status](https://travis-ci.com/sartography/SpiffWorkflow.svg?branch=master)](https://travis-ci.org/sartography/SpiffWorkflow)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=sartography_SpiffWorkflow&metric=alert_status)](https://sonarcloud.io/dashboard?id=sartography_SpiffWorkflow)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=sartography_SpiffWorkflow&metric=coverage)](https://sonarcloud.io/dashboard?id=sartography_SpiffWorkflow)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=sartography_SpiffWorkflow&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=sartography_SpiffWorkflow)
[![Documentation Status](https://readthedocs.org/projects/spiffworkflow/badge/?version=latest)](http://spiffworkflow.readthedocs.io/en/latest/?badge=latest)
[![Issues](https://img.shields.io/github/issues/sartography/spiffworkflow)](https://github.com/sartography/SpiffWorkflow/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/sartography/spiffworkflow)](https://github.com/sartography/SpiffWorkflow/pulls)

## Code style

[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)


## Dependencies
We've worked to minimize external dependencies.  We rely on lxml for parsing
XML Documents, and there is some legacy support for Celery, but it is not
core to the implementation, it is just a way to interconnect these systems.
<b>Built with</b>
- [lxml](https://lxml.de/)
- [celery](https://docs.celeryproject.org/en/stable/)

## Features
* __BPMN__ - support for parsing BPMN diagrams, including the more complex
components, like pools and lanes, multi-instance tasks, sub-workflows, timer
events, signals, messages, boudary events and looping.
* __DMN__ - We have a baseline implementation of DMN that is well integrated
with our Python Execution Engine.
* __Forms__ - forms, including text fields, selection lists, and most every other
thing you can be extracted from the Camunda xml extension, and returned as
json data that can be used to generate forms on the command line, or in web
applications (we've used Formly to good success)
* __Python Workflows__ - We've retained support for building workflows directly
in code, or running workflows based on a internal json data structure.

_A complete list of the latest features is available with our [release notes](https://github.com/sartography/SpiffWorkflow/releases/tag/1.0) for
version 1.0._

## Code Examples and Documentation
Detailed documentation is available on [ReadTheDocs](https://spiffworkflow.readthedocs.io/en/latest/)
Also, checkout our [example application](https://github.com/sartography/SpiffExample), which we
reference extensively from the Documentation.

## Installation
```
pip install spiffworkflow
```

## Tests
```
cd tests
./run_suite.sh
```

## Releases

Be sure to edit the conf.py, and update the release tag: doc/conf.py
And also edit setup.py and assure that has the same release tag.
New versions of SpiffWorkflow are automatically published to PyPi whenever
a maintainer of our GitHub repository creates a new release on  GitHub.  This
is managed through GitHub's actions.  The configuration of which can be
found in .github/workflows/....
Just create a release in GitHub that mathches the release number in doc/conf.py

## Contribute
Pull Requests are and always will be welcome!

Please check your formatting, assure that all tests are passing, and include
any additional tests that can demonstrate the new code you created is working
as expected.  If applicable, please reference the issue number in your pull
request.

## Credits and Thanks

Samuel Abels (@knipknap) for creating SpiffWorkflow and maintaining it for over
a decade.

Matthew Hampton (@matthewhampton) for his initial contributions around BPMN
parsing and execution.

The University of Virginia for allowing us to take on the mammoth task of
building a general-purpose workflow system for BPMN, and allowing us to
contribute that back to the open source community. In particular, we would like
to thank [Ron Hutchins](https://www.linkedin.com/in/ron-hutchins-b19603123/),
for his trust and support.  Without him our efforts would not be possible.

Bruce Silver, the author of BPMN Quick and Easy Using Method and Style, whose
work we referenced extensively as we made implementation decisions and
educated ourselves on the BPMN and DMN standards.

The BPMN.js library, without which we would not have the tools to effectively
build out our models, embed an editor in our application, and pull this mad
mess together.

Kelly McDonald (@w4kpm) who dove deeper into the core of SpiffWorkflow than
anyone else, and was instrumental in helping us get some of these major
enhancements working correctly.

Thanks also to the many contributions from our community.  Large and small.
From Ziad (@ziadsawalha) in the early days to Elizabeth (@essweine) more
recently.  It is good to be a part of this long lived and strong
community.


## Support
Commercial support for SpiffWorkflow is available from
[Sartography](https://sartography.com)

## License
GNU LESSER GENERAL PUBLIC LICENSE
