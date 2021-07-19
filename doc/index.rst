.. image:: https://travis-ci.com/sartography/SpiffWorkflow.svg?branch=master
    :target: https://travis-ci.org/sartography/SpiffWorkflow

.. image:: https://sonarcloud.io/api/project_badges/measure?project=sartography_SpiffWorkflow&metric=alert_status
    :target: https://sonarcloud.io/dashboard?id=sartography_SpiffWorkflow

.. image:: https://sonarcloud.io/api/project_badges/measure?project=sartography_SpiffWorkflow&metric=coverage
    :target: https://sonarcloud.io/dashboard?id=sartography_SpiffWorkflow
    :alt: Coverage

.. image:: https://img.shields.io/github/stars/sartography/SpiffWorkflow.svg
    :target: https://github.com/sartography/SpiffWorkflow/stargazers

.. image:: https://img.shields.io/github/license/sartography/SpiffWorkflow.svg
    :target: https://github.com/sartography/SpiffWorkflow/blob/master/COPYING

What is SpiffWorkflow?
======================

Spiff Workflow is a workflow engine implemented in pure Python.
It is based on the excellent work of the
`Workflow Patterns initiative <http://www.workflowpatterns.com/>`_.
Its main design goals are the following:

- Directly support as many of the patterns of workflowpatterns.com as possible.
- Map those patterns into workflow elements that are easy to understand by a user in a workflow GUI editor.
- Provide a clean Python API.

You can find a list of supported workflow patterns in :ref:`features`.

In addition, Spiff Workflow provides a parser and workflow emulation
layer that can be used to create executable Spiff Workflow specifications
from Business Process Model and Notation (BPMN) documents. See :doc:`/bpmn/intro`.

License
-------
Spiff Workflow is published under the terms of the
`GNU Lesser General Public License (LGPL) Version 3 <https://www.gnu.org/licenses/lgpl-3.0.txt>`_.

Contents
--------
.. toctree::
   :maxdepth: 2

   basics
   bpmn/index
   tutorial/index
   custom-tasks/index
   internals
   features

