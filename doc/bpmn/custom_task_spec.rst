Implementing a Custom Task Spec
-------------------------------

Suppose we wanted to manage Timer Start Events outside of SpiffWorkflow.  If we have a process loaded up and running that
starts with a timer, the timer waits until the event occurs; this might be days or weeks later.

Of course, we can always check that it's waiting and serialize the workflow until that time.  However, we might decide that
we don't want SpiffWorkflow to manage this at all.  We could do this with a custom task spec.

First we'll create a new class

.. code:: python

    from SpiffWorkflow.bpmn.specs.event_definitions import NoneEventDefinition
    from SpiffWorkflow.bpmn.specs.event_definitions.timer import TimerEventDefinition
    from SpiffWorkflow.bpmn.specs.mixins import StartEventMixin
    from SpiffWorkflow.spiff.specs import SpiffBpmnTask

    class CustomStartEvent(StartEventMixin, SpiffBpmnTask):

        def __init__(self, wf_spec, bpmn_id, event_definition, **kwargs):

            if isinstance(event_definition, TimerEventDefinition):
                super().__init__(wf_spec, bpmn_id, NoneEventDefinition(), **kwargs)
                self.timer_event = event_definition
            else:
                super().__init__(wf_spec, bpmn_id, event_definition, **kwargs)
                self.timer_event = None

When we create our custom event, we'll check to see if we're creating a Start Event with a :code:`TimerEventDefinition`, and
if so, we'll replace it with a :code:`NoneEventDefinition`.  There are three different types of Timer Events, so we'll use
the base class for all three to make sure we account for TimeDate, Duration, and Cycle.

.. note::

    Our class inherits from two classes.  We import a mixin class that defines generic BPMN Start Event behavior from
    :code:`StartEventMixin` in the :code:`bpmn` package and the :code:`SpiffBpmnTask` from the :code:`spiff` package, which
    extends the default :code:`BpmnSpecMixin`.
    
    We've split the basic behavior for specific BPMN tasks from the :code:`BpmnSpecMixin` to make it easier to extend
    them without running into MRO issues.

    In general, if you implement a custom task spec, you'll need to inherit from bases of both categories.

Whenever we create a custom task spec, we'll need to create a converter for it so that it can be serialized.

.. code:: python

    from SpiffWorkflow.bpmn.serializer import BpmnWorkflowSerializer
    from SpiffWorkflow.bpmn.serializer.default import EventConverter
    from SpiffWorkflow.spiff.serializer.task_spec import SpiffBpmnTaskConverter
    from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG

    class CustomStartEventConverter(SpiffBpmnTaskConverter):

        def __init__(self, registry):
            super().__init__(CustomStartEvent, registry)

        def to_dict(self, spec):
            dct = super().to_dict(spec)
            if spec.timer_event is not None:
                dct['event_definition'] = self.registry.convert(spec.timer_event)
            else:
                dct['event_definition'] = self.registry.convert(spec.event_definition)
            return dct

        
    DEFAULT_CONFIG['task_specs'].remove(StartEventConverter)
    DEFAULT_CONFIG['task_specs'].append(CustomStartEventConverter)
    registry = BpmnWorkflowSerializer.configure(DEFAULT_CONFIG)
    serializer = BpmnWorkflowSerializer(registry)

Our converter will inherit from the :code:`SpiffBpmnTaskConverter`, since that's our base generic BPMN mixin class.

The :code:`SpiffBpmnTaskConverter` itself inherits from 
:code:`SpiffWorkflow.bpmn.serializer.helpers.task_spec.BpmnTaskSpecConverter`. which provides some helper methods for
extracting standard attributes from tasks; the :code:`SpiffBpmnTaskConverter` does the same for extensions from the
:code:`spiff` package.

We don't have to do much -- all we do is replace the event definition with the original.  The timer event will be
moved when the task is restored, and this saves us from having to write a custom parser.

.. note::

    It might be better have the class's init method take both the event definition to use *and* the timer event
    definition.  Unfortunately, our parser is not terribly intuitive or easily extendable, so I've done it this
    way to make this a little easier to follow.

When we create our serializer, we need to tell it about this task.  We'll remove the converter for the standard Start
Event and add the one we created to the configuration.  We then get a registry of classes that the serializer knows
about that includes our custom spec, as well as all the other specs and initialize the serializer with it.

.. note::

    The reason there are two steps involved (regurning a registry and *then* passing it to the serializer) rather
    that using the configuration directly is to allow further customization of the :code:`registry`.  Workflows
    can contain arbtrary data, we want to provide developers the ability to serialization code for any object.  See
    :ref:`serializing_custom_objects` for more information about how this works.

Finally, we have to update our parser:

.. code:: python

    from SpiffWorkflow.spiff.parser import SpiffBpmnParser
    from SpiffWorkflow.spiff.parser.event_parsers import StartEventParser
    from SpiffWorkflow.bpmn.parser.util import full_tag

    parser = SpiffBpmnParser()
    parser.OVERRIDE_PARSER_CLASSES[full_tag('startEvent')] = (StartEventParser, CustomStartEvent)

The parser contains class attributes that define how to parse a particular element and the class that should be used to
create the task spec, so rather than pass these in as arguments, we create a parser and then update the values it
will use.  This is a bit unintuitive, but that's how it works.

Fortunately, we were able to reuse an existing Task Spec parser, which simplifies the process quite a bit.

Having created a parser and serializer, we could create a configuration module and instantiate an engine with these
components.

There is a very simple diagram :bpmn:`timer_start.bpmn` with the process ID `timer_start` with a Start Event
with a Duration Timer of one day that can be used to illustrate how the custom task works.  If you run this workflow
with any of the configurations provided, you'll see a `WAITING` Start Event; if you use the parser and serializer we
just created, you'll be propmted to complete the User Task immediately.
