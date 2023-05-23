Implementing a Custom Task Spec
-------------------------------

Suppose we wanted to manage Timer Start Events outside of SpiffWorkflow.  If we have a process loaded up and running that
starts with a timer, the timer waits until the event occurs; this might be days or weeks later.

Of course, we can always check that it's waiting and serialize the workflow until that time.  However, we might decide that
we don't want SpiffWorkflow to manage this at all.  We could do this with a custom task spec.

First we'll create a new class

.. code:: python

    from SpiffWorkflow.bpmn.specs.event_definitions import TimerEventDefinition, NoneEventDefinition
    from SpiffWorkflow.bpmn.specs.mixins.events.start_event import StartEvent
    from SpiffWorkflow.spiff.specs.spiff_task import SpiffBpmnTask

    class CustomStartEvent(StartEvent, SpiffBpmnTask):

        def __init__(self, wf_spec, bpmn_id, event_definition, **kwargs):

            if isinstance(event_definition, TimerEventDefinition):
                super().__init__(wf_spec, bpmn_id, NoneEventDefinition(), **kwargs)
                self.timer_event = event_definition
            else:
                super().__init__(wf_spec, bpmn_id, event_definition, **kwargs)
                self.timer_event = None

When we create our custom event, we'll check to see if we're creating a Start Event with a TimerEventDefinition, and if so,
we'll replace it with a NoneEventDefinition.

.. note::

    Our class inherits from two classes.  We import a mixin class that defines generic BPMN Start Event behavior from
    :code:`StartEvent` in the :code:`bpmn` package and the :code:`SpiffBpmnTask` from the :code:`spiff` package, which
    extends the default :code:`BpmnSpecMixin`.
    
    We've split the basic behavior for specific BPMN tasks from the :code:`BpmnSpecMixin` to make it easier to extend
    them without running into MRO issues.

    In general, if you implement a custom task spec, you'll need to inherit from bases of both categories.

Whenever we create a custom task spec, we'll need to create a converter for it so that it can be serialized.

.. code:: python

    from SpiffWorkflow.bpmn.serializer.workflow import BpmnWorkflowSerializer
    from SpiffWorkflow.bpmn.serializer.task_spec import StartEventConverter
    from SpiffWorkflow.spiff.serializer.task_spec import SpiffBpmnTaskConverter
    from SpiffWorkflow.spiff.serializer.config import SPIFF_SPEC_CONFIG

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

        
    SPIFF_SPEC_CONFIG['task_specs'].remove(StartEventConverter)
    SPIFF_SPEC_CONFIG['task_specs'].append(CustomStartEventConverter)

    wf_spec_converter = BpmnWorkflowSerializer.configure_workflow_spec_converter(SPIFF_SPEC_CONFIG)
    serializer = BpmnWorkflowSerializer(wf_spec_converter)

Our converter will inherit from the :code:`SpiffBpmnTaskConverter`, since that's our base generic BPMN mixin class.

The :code:`SpiffBpmnTaskConverter` ultimately inherits from 
:code:`SpiffWorkflow.bpmn.serializer.helpers.task_spec.BpmnTaskSpecConverter`. which provides some helper methods for
extracting standard attributes from tasks; the :code:`SpiffBpmnTaskConverter` does the same for extensions from the
:code:`spiff` package.

We don't have to do much -- all we do is replace the event definition with the original.  The timer event will be
moved when the task is restored.

.. note::

    It might be better have the class's init method take both the event definition to use *and* the timer event
    definition.  Unfortunately, our parser is not terribly intuitive or easily extendable, so I've done it this
    way to make this a little easier to follow.

When we create our serializer, we need to tell it about this task.  We'll remove the converter for the standard Start
Event and add the one we created to the confiuration and create the :code:`workflow_spec_converter` from the updated
config.

.. note::

    We have not instantiated our converter class.  When we call :code:`configure_workflow_spec_converter` with a
    configuration (which is essentially a list of classes, split up into sections for organizational purposes),
    *it* instantiates the classes for us, using the same `registry` for every class.  At the end of the configuration
    if returns this registry, which now knows about all of the classes that will be used for SpiffWorkflow
    specifications.  It is possible to pass a separately created :code:`DictionaryConverter` preconfigured with
    other converters; in that case, it will be used as the base `registry`, to which specification conversions will
    be added.
    
Because we've built up the `registry` in such a way, we can make use of the :code:`registry.convert` and
:code:`registry.restore` methods rather than figuring out how to serialize them.  We can use these methods on any
objects that SpiffWorkflow knows about.

See :doc:`advanced` for more information about the serializer.

Finally, we have to update our parser:

.. code:: python

    from SpiffWorkflow.spiff.parser.event_parsers import StartEventParser
    from SpiffWorkflow.spiff.parser.process import SpiffBpmnParser
    from SpiffWorkflow.bpmn.parser.util import full_tag

    parser = SpiffBpmnParser()
    parser.OVERRIDE_PARSER_CLASSES[full_tag('startEvent')] = (StartEventParser, CustomStartEvent)

The parser contains class attributes that define how to parse a particular element and the class that should be used to
create the task spec, so rather than pass these in as arguments, we create a parser and then update the values it
will use.  This is a bit unintuitive, but that's how it works.

Fortunately, we were able to reuse an existing Task Spec parser, which simplifies the process quite a bit.

Having created a parser and serializer, we could replace the ones we pass in the the :code:`SimpleBpmnRunner` with these.

I am going to leave creating a script that makes use of them to readers of this document, as it should be clear enough
how to do.

There is a very simple diagram `bpmn/tutorial/timer_start.bpmn` with the process ID `timer_start` with a Start Event
with a Duration Timer of one day that can be used to illustrate how the custom task works.  If you run this workflow
with `spiff-bpmn-runner.py`, you'll see a `WAITING` Start Event; if you use the parser and serializer we just created,
you'll be propmted to complete the User Task immediately.