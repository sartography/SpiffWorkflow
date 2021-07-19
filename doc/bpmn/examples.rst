Basic Concepts, Example Code,and Diagrams
=========================================

The basic idea of SpiffWorkflow is that you can use it to write an interpreter
in Python that creates business applications from BPMN models.

In this section of the documentation, we introduce that process.

.. sidebar:: Example Code

  All the Python code and BPMN models used here are available in an example
  project called `SpiffExample <https://github.com/sartography/SpiffExample>`_

Basic Example
--------------
This model is found in BasicExample.bpmn.

In this example, we examine one of the simplest BPMN workflows. There is a start event, an activity
called Trip Info with a UserTask, and an end event.

.. image:: images/basic_example.png
   :scale: 25%
   :align: center

User tasks can include forms that ask the user questions. When you click on a
user task in a BPMN modeler, the Properties Panel includes a form tab. Use this
tab to build your questions.

In this flow the user is answering two questions : where they are going, and whether they like spam.

In the image below you can see information about the *location* question associated with the Trip Info user task. We are using an enumeration type with 3 possible answers; cabin, hotel, and camping. Note that there is also a *spam* form field for the second question.

It is recommended that you add a default value in case the user does not input a variable
that is recognized.

.. image:: images/basic_example_form.png

Example Code
------------
We can use the code in `ExampleCode.py <https://github.com/sartography/SpiffExample/blob/master/ExampleCode.py>`_ to run the workflow in our BPMN model.

First, we have some imports.

.. code:: python

    from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
    from SpiffWorkflow.camunda.parser.CamundaParser import CamundaParser
    from SpiffWorkflow.camunda.specs.UserTask import EnumFormField, UserTask


Next, we instantiate a parser, read the BPMN file, and grab the spec.

.. code:: python

    parser = CamundaParser()
    parser.add_bpmn_file('BasicExample.bpmn')
    spec = parser.get_spec('BasicExample')

[Note that we hardcoded the name of the BPMN file and the spec. We will return to this below.]

Next, we create a workflow instance from the spec using BPMNWorkflow. This is
the engine that does the work for us. It manages the tasks and branches, and
holds the data for a working workflow.

.. code:: python

    workflow = BpmnWorkflow(spec)

We use do_engine_steps() to run all tasks the engine can complete on its own.
I.e., without user input. Then, we gather the user tasks.

.. code:: python

    workflow.do_engine_steps()
    ready_tasks = workflow.get_ready_user_tasks()

The next section of code loops through the user tasks, displays their forms, and completes each task.

.. code:: python

    while len(ready_tasks) > 0:
        for task in ready_tasks:
            if isinstance(task.task_spec, UserTask):
               show_form(task)
               print(task.data)
            else:
                print("Complete Task ", task.task_spec.name)
            workflow.complete_task_from_id(task.id)

ExampleCode.py also defines the function *show_form* that builds an input prompt from the form, displays the prompt, and updates the workflow data with the user response.

.. code:: python

    def show_form(task):
        model = {}
        form = task.task_spec.form

        if task.data is None:
            task.data = {}

        for field in form.fields:
            prompt = field.label
            if isinstance(field, EnumFormField):
                prompt += "? (Options: " + ', '.join([str(option.id) for option in field.options]) + ")"
            prompt += "? "
            answer = input(prompt)
            if field.type == "long":
                answer = int(answer)
            task.update_data_var(field.id,answer)

Here is some sample output when running the code.

.. code:: bash

  $ python ExampleCode.py
  Where are you going? (Options: cabin, hotel, camping)? camping
  ['location']
  Do you like spam? Yes
  ['spam']
  {'location': 'camping', 'spam': 'Yes'}
  {'location': 'camping', 'spam': 'Yes'}


Exclusive Gateway Example
--------------------------
This model is found in `ExclusiveGateway.bpmn <https://github.com/sartography/SpiffExample/blob/master/ExclusiveGateway.bpmn>`.

In an exclusive gateway, exactly one alternative can be selected. The token runs along the sequence flow whose condition is met first. The response you get depends on which path you take.

In this example, the path taken depends on the response to the “Do you like spam?” question in the previous user task . If you answered no, you will ONLY be asked for bad spam brands. If you answered yes, you will ONLY be asked good spam brands.

.. image:: images/ExclusiveGateway.png
   :scale: 25%
   :align: center

With a little modification, we can use the python in ExampleCode.py to run this model.

Remember that we hardcoded the name of the BPMN file and the spec. To run the exclusive gateway model, we just need to edit the two lines to the new file and spec.

Change

.. code:: python

    parser.add_bpmn_file('Basicexample.bpmn')
    spec = parser.get_spec('Basicexample')

to

.. code:: python

    parser.add_bpmn_file('ExclusiveGateway.bpmn')
    spec = parser.get_spec('ExclusiveGateway')

and run ExampleCode.py.

Here is some sample output for ExclusiveGateway.bpmn

.. code:: bash

    $ python ExampleCode.py
    Where are you going? (Options: cabin, hotel, camping)? hotel
    ['location']
    Do you like spam? yes
    ['spam']
    {'location': 'hotel', 'spam': 'yes'}
    What is a good spam brand? SpamX
    ['good brand']
    {'location': 'hotel', 'spam': 'yes', 'good brand': 'SpamX'}
    {'location': 'hotel', 'spam': 'yes', 'good brand': 'SpamX'}


Parallel Gateway Example
-------------------------
This model is found in `ParallelGateway.bpmn <https://github.com/sartography/SpiffExample/blob/master/parallelgateway.bpmn>`.

A parallel or AND gateway creates parallel paths without checking any conditions. This means that each outgoing sequence flow becomes active upon the execution of a parallel gateway

In this workflow, you will be prompted for both a good and bad example of spam.

.. image:: images/ParallelGateway.png
   :scale: 25%
   :align: center

To run this code, edit ExampleCode.py to use *ParallelGateway.bpmn* and *ParallelGateway*.

.. code:: python

    parser.add_bpmn_file('ParallelGateway.bpmn')
    spec = parser.get_spec('ParallelGateway')


Here is sample output.

.. code:: bash

    $ python ExampleCode.py
    Where are you going? (Options: cabin, hotel, camping)? cabin
    ['location']
    Do you like spam? yes
    ['spam']
    {'location': 'cabin', 'spam': 'yes'}
    What is a bad spam brand? Spambolina
    ['bad brand']
    {'location': 'cabin', 'spam': 'yes', 'bad brand': 'Spambolina'}
    What is a good spam brand? SpamX
    ['good brand']
    {'location': 'cabin', 'spam': 'yes', 'good brand': 'SpamX'}
    {'location': 'cabin', 'spam': 'yes', 'good brand': 'SpamX', 'bad brand': 'Spambolina'}


Script Example
-----------------
This model is found in `ScriptExample.bpmn <https://github.com/sartography/SpiffExample/blob/master/ScriptExample.bpmn>`.

.. sidebar:: Setting up a script task

  To create a script task in a BPMN modeler, you drag over a task from the object bar and then right click on the
  task, use the wrench and select a script task from the options.  Once you have a script task selected, use the
  'inline script' option in the options bar on the right and put in the code that you want to run. When using scripts,
  you can interact with all of the data that has been put into the task.data object during the workflow.

  .. image:: images/script_task.png
     :align: center


A Script Task is executed by a business process engine. In our example, it's do_engine_steps(). The modeler or implementer defines a script in a language that the engine can interpret. For us, this is python.

When the Task is ready to start, the engine will execute the script. When the script is completed, the Task will also be completed. These are good to use when a task can be performed automatically.


.. image:: images/Scriptsexample.png
   :scale: 25%
   :align: center

In this example, the script prints something based on whether or not you like spam.

To run this code, edit ExampleCode.py to use *ScriptExample.bpmn* and *ScriptExample*.

.. code:: python

    parser.add_bpmn_file('ScriptExample.bpmn')
    spec = parser.get_spec('ScriptExample')


Here is sample output.

.. code:: bash

    $ python ExampleCode.py
    Where are you going? (Options: cabin, hotel, camping)? cabin
    ['location']
    Do you like spam? yes
    ['spam']
    {'location': 'cabin', 'spam': 'yes'}
    Yeah Spam!!
    {'location': 'cabin', 'spam': 'yes'}


Multi-Instance Example
-------------------------
This model is found in `MultiInstance.bpmn <https://github.com/sartography/SpiffExample/blob/master/MultiInstance.bpmn>`.

Multi-instance activities are represented by three horizontal or vertical lines at the bottom-center of the activity and task symbol. The number of times that the activity completes is defined by the number of items that exist in the collection. This is different from other looping mechanisms that must check a condition every time the loop completes in order to determine if it should continue looping.

Three vertical lines indicate that the multi-instance activity is parallel.  This means that the
activity can be completed for each item in the collection in no particular order.

Three horizontal lines indicate that the multi-instance activity is sequential. This means that the activity must complete for each item in the order that they are received within the collection.

.. image:: images/multi_instance_array.png

In this example, the first activity is a UserTask where we ask for the family size. We then use that number to go through the multi-instance. The first multi-instance is parallel, which means that you can add the names in any order. The second multi-instance is sequential and will loop through the names from the previous task in the order they were received.

.. code:: bash

    $ python ExampleCode.py
    Family Size? 2
    ['Family', 'Size']
    {'Family': {'Size': 2}}
    First Name? John
    ['FamilyMember', 'FirstName']
    {'FamilyMember': {'FirstName': 'John'}, 'Family': {'Size': 2}}
    First Name? Jane
    ['FamilyMember', 'FirstName']
    {'FamilyMember': {'FirstName': 'Jane'}, 'Family': {'Size': 2, 'Members': {1: {'FirstName': 'John'}}}}
    Birthday? Johnday
    ['CurrentFamilyMember', 'Birthdate']
    {'CurrentFamilyMember': {'FirstName': 'John', 'Birthdate': 'Johnday'}, 'Family': {'Size': 2, 'Members': {1: {'FirstName': 'John'}, 2: {'FirstName': 'Jane'}}}, 'FamilyMember': {'FirstName': 'John'}}
    Birthday? Janeday
    ['CurrentFamilyMember', 'Birthdate']
    {'CurrentFamilyMember': {'FirstName': 'Jane', 'Birthdate': 'Janeday'}, 'Family': {'Size': 2, 'Members': {1: {'FirstName': 'John', 'Birthdate': 'Johnday'}, 2: {'FirstName': 'Jane'}}}, 'FamilyMember': {'FirstName': 'John'}}
    {'Family': {'Size': 2, 'Members': {1: {'FirstName': 'John', 'Birthdate': 'Johnday'}, 2: {'FirstName': 'Jane', 'Birthdate': 'Janeday'}}}, 'FamilyMember': {'FirstName': 'John'}}

This is somewhat problematic, because the user must remember the order in which they entered the names. In the chapter on Jinja2, we cover multi-instance in more depth and use Templates to solve our problem.


MultiInstance Notes
-------------------

A subset of MultiInstance and Looping Tasks are supported. Notably,
the completion condition is not currently supported.

The following definitions should prove helpful

**loopCardinality** - This variable can be a text representation of a
number - for example '2' or it can be the name of a variable in
task.data that resolves to a text representation of a number.
It can also be a collection such as a list or a dictionary. In the
case that it is a list, the loop cardinality is equal to the length of
the list and in the case of a dictionary, it is equal to the list of
the keys of the dictionary.

If loopCardinality is left blank and the Collection is defined, or if
loopCardinality and Collection are the same collection, then the
MultiInstance will loop over the collection and update each element of
that collection with the new information. In this case, it is assumed
that the incoming collection is a dictionary, currently behavior for
working with a list in this manner is not defined and will raise an error.

**Collection** This is the name of the collection that is created from
the data generated when the task is run. Examples of this would be
form data that is generated from a UserTask or data that is generated
from a script that is run. Currently the collection is built up to be
a dictionary with a numeric key that corresponds to the place in the
loopCardinality. For example, if we set the loopCardinality to be a
list such as ['a','b','c] the resulting collection would be {1:'result
from a',2:'result from b',3:'result from c'} - and this would be true
even if it is a parallel MultiInstance where it was filled out in a
different order.

**Element Variable** This is the variable name for the current
iteration of the MultiInstance. In the case of the loopCardinality
being just a number, this would be 1,2,3, . . .  If the
loopCardinality variable is mapped to a collection it would be either
the list value from that position, or it would be the value from the
dictionary where the keys are in sorted order.  It is the content of the
element variable that should be updated in the task.data. This content
will then be added to the collection each time the task is completed.

Example:
  In a sequential MultiInstance, loop cardinality is ['a','b','c'] and elementVariable is 'myvar'
  then in the case of a sequential multiinstance the first call would
  have 'myvar':'a' in the first run of the task and 'myvar':'b' in the
  second.

Example:
  In a Parallel MultiInstance, Loop cardinality is a variable that contains
  {'a':'A','b':'B','c':'C'} and elementVariable is 'myvar' - when the multiinstance is ready, there
  will be 3 tasks. If we choose the second task, the task.data will
  contain 'myvar':'B'.

Updating Data
-------------

While there may be some MultiInstances that will not result in any
data, most of the time there will be some kind of data generated that
will be collected from the MultiInstance. A good example of this is a
UserTask that has an associated form or a script that will do a lookup
on a variable.

Each time the MultiInstance task generates data, the method
task.update_data(data) should be called where data is the data
generated. The 'data' variable that is passed in is assumed to be a
dictionary that contains the element variable. Calling task.update_data(...)
will ensure that the MultiInstance gets the correct data to include in the
collection. The task.data is also updated with the dictionary passed to
this method.

Example:
  In a Parallel MultiInstance, Loop cardinality is a variable that contains
  {'a':'A','b':'B','c':'C'} and elementVariable is 'myvar'.
  If we choose the second task, the task.data will contain 'myvar':{'b':'B'}.
  If we wish to update the data, we would call task.update_data('myvar':{'b':'B2'})
  When the task is completed, the task.data will now contain:
  {'a':'A','b':'B2','c':'C'}

Looping Tasks
-------------

A looping task sets the cardinality to 25 which is assumed to be a sane maximum value. The looping task will add to the collection each time it is processed if you are updating data.

To halt the looping the task.terminate_loop()

Each time task.complete() is called (or workflow.complete_task_by_id(task.id) ), the task will again present as READY until either the cardinality is exausted, or task.terminate_loop() is called.



