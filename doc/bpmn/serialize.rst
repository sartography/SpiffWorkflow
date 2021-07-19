Serialize / Deserialize
===================================

All of our examples so far have come in the context where we will run the workflow from beginning to end in one
setting. This may not always be the case, we may be executing the workflow in the context of a web server where we
may have a user request a web page where we open a specific workflow that we may be in the middle of, do one step of
that workflow and then the user may be back in a few minutes, or maybe a few hours depending on the application.

It is important then that we can save and load the workflow, including all of the data and information about where
the user is at in the workflow.

SpiffWorkflow has a few methods to help us with this.

.. code:: python

   state = BpmnSerializer().serialize_workflow(self.workflow, include_spec=include_spec)
   workflow = BpmnSerializer().deserialize_workflow(state, workflow_spec=None)

The first line will pack up the entire state of the workflow and put it in the variable 'state' and the second line
will take what is in the 'state' variable and re-build the workflow.

Lets re-use our example from the jinja documentation to show how we would put this into practice.

.. figure:: images/multi_instance_array.png
   :align: center

   Example Workflow

In that section, we used the ExampleCode-multi.py code to show how we could incorporate Jinja documentation string
into a workflow. We'll take that exact same code and add the lines above (plus some support code) to make sure that
if we get interrupted, our workflow can pick up exactly where it left off.

Where we used to have

.. code:: python
   :number-lines: 31

    x = CamundaParser()
    x.add_bpmn_file('multi_instance_array.bpmn')
    spec = x.get_spec('MultiInstanceArray')

we change it to this

.. code:: python
   :number-lines: 31

    if os.path.exists('ExampleSaveRestore.js'):
        f = open('ExampleSaveRestore.js')
        state = f.read()
        f.close()
        workflow = BpmnSerializer().deserialize_workflow(
                    state, workflow_spec=None)
    else:
        x = CamundaParser()
        x.add_bpmn_file('multi_instance_array.bpmn')
        spec = x.get_spec('MultiInstanceArray')

.. sidebar:: Work to do

   This works fine for the usual UserTask multi-instances, but I suspect we still have some work to do with other,
   more esoteric things like a Script MultiInstance or a CallActivity MultiInstance

Essentially, we look for a file that we save that contains the state in it, and if we find it, we re-load the
workflow and use that, if not, we start the whole process from the beginning.

Please note that when the workflow is entirely complete, we will save the state and if we run it again, it will
happily find the state file and try to run a completed workflow. There will be nothing for SpiffWorkflow to do if
this happens!!

This is all well and good, but we need to make sure that there is a state file out there when we have progressed in
the workflow. We do this by adding the following lines

.. code:: python
   :number-lines: 50

        . . .                                                 #
        else:                                                 #
            print("Complete Task ", task.task_spec.name)      #  <- previous code for context
        workflow.complete_task_from_id(task.id)               #
        state = BpmnSerializer().serialize_workflow(workflow,    #
                     include_spec=True)                          #
        f = open('ExampleSaveRestore.js', 'w')                   #   <-- new code
        f.write(state)                                           #
        f.close()                                                #

So, each time we do a step, we get the state from the workflow and write that out into the ExampleSaveRestore.js file
. This data is just a big JSON string, and in some cases SpiffWorkflow uses a Python construct known as a 'pickle' to
save more complicated data. (go ahead, look at it.  It won't make much sense, but you can get an idea of what it is
doing)

.. code::

    prompt--> python ExampleCode-multi-save-restore.py
    {}
    Please enter number of people :
    Family Size? 3
    ['Family', 'Size']
    {'Family': {'Size': 3}}
    {'FamilyMember': 1, 'Family': {'Size': 3}}
    Please enter information for family member 1:
    First Name? A
    ['FamilyMember', 'FirstName']
    {'FamilyMember': {'FirstName': 'A'}, 'Family': {'Size': 3}}
    {'FamilyMember': 2, 'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A'}}}}
    Please enter information for family member 2:
    First Name? B
    ['FamilyMember', 'FirstName']
    {'FamilyMember': {'FirstName': 'B'}, 'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A'}}}}
    {'FamilyMember': 3, 'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A'}, 2: {'FirstName': 'B'}}}}
    Please enter information for family member 3:
    First Name? C
    ['FamilyMember', 'FirstName']
    {'FamilyMember': {'FirstName': 'C'}, 'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A'}, 2: {'FirstName': 'B'}}}}
    {'CurrentFamilyMember': {'FirstName': 'A'}, 'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A'}, 2: {'FirstName': 'B'}, 3: {'FirstName': 'C'}}}, 'FamilyMember': {'FirstName': 'B'}}
    Enter Birthday for A
    Birthday? a
    ['CurrentFamilyMember', 'Birthdate']
    {'CurrentFamilyMember': {'FirstName': 'A', 'Birthdate': 'a'}, 'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A'}, 2: {'FirstName': 'B'}, 3: {'FirstName': 'C'}}}, 'FamilyMember': {'FirstName': 'B'}}
    {'CurrentFamilyMember': {'FirstName': 'B'}, 'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A', 'Birthdate': 'a'}, 2: {'FirstName': 'B'}, 3: {'FirstName': 'C'}}}, 'FamilyMember': {'FirstName': 'B'}}
    Enter Birthday for B
    Birthday? ^CTraceback (most recent call last):
      File "ExampleCode-multi-save-restore.py", line 49, in <module>
        show_form(task)
      File "ExampleCode-multi-save-restore.py", line 26, in show_form
        answer = input(prompt)
    KeyboardInterrupt


    prompt--> python ExampleCode-multi-save-restore.py
    {'CurrentFamilyMember': {'FirstName': 'B'}, 'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A', 'Birthdate': 'a'}, 2: {'FirstName': 'B'}, 3: {'FirstName': 'C'}}}, 'FamilyMember': {'FirstName': 'B'}}
    Enter Birthday for B
    Birthday? b
    ['CurrentFamilyMember', 'Birthdate']
    {'CurrentFamilyMember': {'FirstName': 'B', 'Birthdate': 'b'}, 'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A', 'Birthdate': 'a'}, 2: {'FirstName': 'B'}, 3: {'FirstName': 'C'}}}, 'FamilyMember': {'FirstName': 'B'}}
    {'CurrentFamilyMember': {'FirstName': 'C'}, 'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A', 'Birthdate': 'a'}, 2: {'FirstName': 'B', 'Birthdate': 'b'}, 3: {'FirstName': 'C'}}}, 'FamilyMember': {'FirstName': 'B'}}
    Enter Birthday for C
    Birthday? c
    ['CurrentFamilyMember', 'Birthdate']
    {'CurrentFamilyMember': {'FirstName': 'C', 'Birthdate': 'c'}, 'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A', 'Birthdate': 'a'}, 2: {'FirstName': 'B', 'Birthdate': 'b'}, 3: {'FirstName': 'C'}}}, 'FamilyMember': {'FirstName': 'B'}}
    {'Family': {'Size': 3, 'Members': {1: {'FirstName': 'A', 'Birthdate': 'a'}, 2: {'FirstName': 'B', 'Birthdate': 'b'}, 3: {'FirstName': 'C', 'Birthdate': 'c'}}}, 'FamilyMember': {'FirstName': 'B'}}

This is pretty verbose, but you can see where we were able to break the code, re-run the Python file, and pick up exactly where we left off, and see that all of the data that we had previously is still the same as it was when we saved the file. Pretty Spiffy!!

