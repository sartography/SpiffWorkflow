.. image:: https://travis-ci.org/knipknap/SpiffWorkflow.svg?branch=master
    :target: https://travis-ci.org/knipknap/SpiffWorkflow

.. image:: https://coveralls.io/repos/github/knipknap/SpiffWorkflow/badge.svg?branch=master
    :target: https://coveralls.io/github/knipknap/SpiffWorkflow?branch=master

.. image:: https://lima.codeclimate.com/github/knipknap/SpiffWorkflow/badges/gpa.svg
    :target: https://lima.codeclimate.com/github/knipknap/SpiffWorkflow
    :alt: Code Climate

.. image:: https://img.shields.io/github/stars/knipknap/SpiffWorkflow.svg   
    :target: https://github.com/knipknap/SpiffWorkflow/stargazers

.. image:: https://img.shields.io/github/license/knipknap/SpiffWorkflow.svg
    :target: https://github.com/knipknap/SpiffWorkflow/blob/master/COPYING

|
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
from Business Process Model and Notation (BPMN) documents. See :ref:`bpmn_page`.

License
-------
Spiff Workflow is published under the terms of the
`GNU Lesser General Public License (LGPL) Version 3 <https://www.gnu.org/licenses/lgpl-3.0.txt>`_.

Contents
--------

.. toctree::
   :maxdepth: 2

   basics
   tutorial/index
   custom-tasks/index
   bpmn
   internals
   features
   API Documentation<modules>
