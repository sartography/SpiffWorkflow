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


SpiffWorkflow allows your python application to process BPMN diagrams (think
of them as very powerful flow charts,  See :doc:`/bpmn/intro`.) to accomplish
what would otherwise require writing a lot of complex business logic in your
code. You can use these diagrams to accomplish a number of tasks, such as:

 - Creating a questionnaire with multiple complex paths
 - Implement an approval process that requires input from multiple users
 - Allow non-programmers to modify the flow and behavior of your application.

SpiffWorkflow is based on the excellent work of the
`Workflow Patterns initiative <http://www.workflowpatterns.com/>`_.
Its main design goals are the following:

- Directly support as many of the patterns of workflowpatterns.com as possible.
- Map those patterns into workflow elements that are easy to understand by a user in a workflow GUI editor.
- Provide a clean Python API.

You can find a list of supported workflow patterns in :ref:`patterns`.


License
-------
Spiff Workflow is published under the terms of the
`GNU Lesser General Public License (LGPL) Version 3 <https://www.gnu.org/licenses/lgpl-3.0.txt>`_.

Contents
--------
.. toctree::
   :maxdepth: 2

   intro
   bpmn/index
   development
   non-bpmn/index

