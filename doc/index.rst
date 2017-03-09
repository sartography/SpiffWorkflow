.. SpiffWorkflow documentation master file, created by
   sphinx-quickstart on Wed Mar  8 07:58:36 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SpiffWorkflow's documentation!
=========================================

Summary
-------

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
Gelatin is published under the terms of the
`GNU Lesser General Public License (LGPL) Version 3 <https://www.gnu.org/licenses/lgpl-3.0.txt>`_.

Contents
--------

.. toctree::
   :maxdepth: 2

   intro
   bpmn
   internals
   features
   API Documentation<modules>
