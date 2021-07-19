Advanced Features
===================================

Our discussion of some of the more advanced features currently available in SpiffWorkflow will revolve around the
following workflow

.. image:: images/MessageBoundary.png

which can be found in the MessageBoundary.bpmn file.

In this workflow are several new concepts:

*  lanes
*  subprocesses
*  message events
*  time events
*  boundary events

Lanes
-------------

Lanes are a method in BPMN to distinguish roles for the workflow and who is
responsible for which actions. In some cases this will be different business
units, and in some cases this will be different individuals - it really depends
on the nature of the workflow.  Within a BPMN editor, this is done by choosing the
'Create pool/participant' option from the toolbar on the left hand side.

Subprocesses
-------------

Subprocesses come in two different flavors, in this workflow we see an 'expanded' subprocess. The other option is an
external subprocess.  In general, subprocesses are a way of grouping work into smaller units. This, in theory, will
help us to re-use sections of business logic, but it will also allow us to treat groups of work as a unit.

Unfortunately, we can't collapse an expanded subprocess within BPMN.js, so really the only purpose of an expanded
subprocess is to do the third thing, that is to treat a group of work as a unit. This is what we have done in our
example workflow. We may want to interrupt the hard work that is going on from our worker and this is accomplished by
a boundary event that will be covered later.

In addition to expanded subprocess, we can have external subprocesses in what is known as a 'CallActivity'. This call
activity is added as a normal task and then the type selected in the configuration menu. This allows us to 'call' a
separate workflow in a different file by referencing the ID of the called workflow. This effectively allows us to
simplify and re-use business logic.

Messaging
----------

BPMN.js allows us to set up message events. These events are only usable within the workflow and may not cross
workflows (even CallActivities). If any kind of cross-workflow coordination is needed, this will need to be handled
through a script activity.

.. sidebar:: TODO

   This may technically not be true - BPMN.js allows you to define a catch event for a message name that you can type
   into the message bar - so . . . we may be able to use it cross workflows - I have created a task for looking into
   this.

Messages allow us to control some workflow events. In the given example, if the boss says to interrupt work, a
message is sent which is later 'caught' by the catch message event.

There are a few ways to use a catch event, one is to use a start/catch event which starts a lane when a message is fired, another way is to have an in-line message catch event which stops the workflow until a message is caught, and the third is a boundary event (covered below).

Time Event
-------------

A time event allows us to create a pause in the workflow, either for a duration or for a specified date/time. A time event can be used in a similar fashion to the message events, that is they can be used as a delayed start event, as an interrupt to the workflow, or as a boundary event

Boundary Events
----------------

Boundary events are a way of stopping or interrupting a subprocess or a task. In the BPMN specification there are multiple events that are defined, but currently SpiffWorkflow only works with the Message and Timer events.

Our example workflow has an example of where a message event gets thrown and then as a boundary event, it interrupts the process that it is assigned to. Timer events would interrupt the process at a specified time rather than when a 'Message Send' event gets thrown.

Boundary events can also be non-interrupting.

Process overview
----------------

With all of these individual concepts defined, we will now explain how they work in concert.

In the MessageBoundary workflow, we have two lanes, one for the Boss and one for the Worker. Later on, we will see how we can request tasks for only the Boss or the Worker

Once the workflow starts, the Boss is repeatedly asked if they would like to interrupt the work. Since the Boss has nothing better to do, they are happy to repeatedly answer this question!

The worker alternates between doing work and taking a break - the break is only a few tenths of a second, and is represented by a 'timer event' showing that the workflow is stopped by the defined length of time. Because the worker is some kind of superhuman,they don't mind taking such a short break nor do they mind doing this forever, or until the boss says that they can stop.  (Actually, the short break is because we actually use this workflow as a test for SpiffWorkflow, and we don't want to wait around on the tests forever)

Once the boss says that 'yes' work should stop, there is a 'Message Throw event' that sends a message to the 'Catch Event'. Because the catch event is on the boundary of a subprocess, this neverending flow of work is interrupted and the entire workflow comes to an end. There are also 'non-interrupting' events that don't interrupt the subworkflow, but will allow for an exception, such as a reason why something was delayed.

Because there are only ever tasks that are ready for the Boss, we can run this entire workflow using the exact same code as we have with our other examples. Next, we will discuss how we can get more information about where we are at in the workflow, and how to get a list of tasks that are ready for each participant in a pool.
