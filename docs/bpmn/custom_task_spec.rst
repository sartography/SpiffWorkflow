Implementing a Custom Task Spec
-------------------------------

Suppose we wanted to manage Timer Start Events outside of SpiffWorkflow.  If we have a process loaded up and running that
starts with a timer, the timer waits until the event occurs; this might be days or weeks later.

Of course, we can always check that it's waiting and serialize the workflow until that time.  However, we might decide that
we don't want SpiffWorkflow to manage this at all.  We could do this with a custom task spec.

The code for this example can be found in :app:`misc/custom_start_event.py`.

There is a very simple diagram :bpmn:`timer_start.bpmn` with the process ID `timer_start` with a Start Event
with a Duration Timer of one day that can be used to illustrate how the custom task works.  If you run this workflow
with any of the configurations provided, you'll see a `WAITING` Start Event; if you use the parser and serializer we
just created, you'll be propmted to complete the User Task immediately.

To run this model with the custom spec:

.. code:: python

    ./runner.py -e spiff_example.misc.custom_start_event add -p timer_start -b bpmn/tutorial/timer_start.bpmn
    ./runner.py -e spiff_example.misc.custom_start_event

First we'll create a new class.

.. note::

    It might be better have the class's init method take both the event definition to use *and* the timer event
    definition.  Unfortunately, our parser is not terribly intuitive or easily extendable, so I've done it this
    way to make this a little easier to follow.

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

When we create our custom spec, we'll check to see if we're creating a Start Event with a :code:`TimerEventDefinition`, and
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
    from SpiffWorkflow.spiff.serializer.task_spec import SpiffBpmnTaskConverter
    from SpiffWorkflow.spiff.serializer import DEFAULT_CONFIG

    class CustomStartEventConverter(SpiffBpmnTaskConverter):

        def to_dict(self, spec):
            dct = super().to_dict(spec)
            dct['event_definition'] = self.registry.convert(spec.event_definition)
            dct['timer_event'] = self.registry.convert(spec.timer_event)
            return dct

        def from_dict(self, dct):
            spec = super().from_dict(dct)
            spec.event_definition = self.registry.restore(dct['event_definition'])
            spec.timer_event = self.registry.restore(dct['timer_event'])
            return spec

Our converter will inherit from the :code:`SpiffBpmnTaskConverter`, since that's our base generic BPMN mixin class.
The parent converter will handle serializing the standard BPMN attributes, as well as attributes added in the
:code:`spiff` package.  There is a similar base converter in the :code:`bpmn.serializer.helpers` package.

A converter needs to implement two methods: :code:`to_dict` (which takes a task spec and returns a JSON-serializable
dictionary of its attributes) and :code:`from_dict` (which takes the dictionary and returns a task spec of the
appropriate type.  We call the base method to do most of the work, and then update the result to reflect the changes
we made, in this case ensuring that both event definitions are handled.  The parent converter also provides  :code:`convert`
and :code:`restore` methods to serialize any object that Spiff's serializer knows how to handle.  For more details about
the serializer, see :doc:`serialization`.

When we create our serializer, we need to tell it about this task.  The serializer is initialized with a mapping
of object class to converter class, so we just need to add an entry for this mapping.

.. code:: python

    SPIFF_CONFIG[CustomStartEvent] = CustomStartEventConverter
    registry = FileSerializer.configure(SPIFF_CONFIG)
    serializer = FileSerializer(dirname, registry=registry)

We also have to tell the parser to use our class instead of the standard class.

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

