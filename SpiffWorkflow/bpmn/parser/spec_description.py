from .util import full_tag

# Having this configurable via the parser makes a lot more sense than requiring a subclass
# This can be further streamlined if we ever replace our parser

SPEC_DESCRIPTIONS = {
    full_tag('startEvent'): 'Start Event',
    full_tag('endEvent'): 'End Event',
    full_tag('userTask'): 'User Task',
    full_tag('task'): 'Task',
    full_tag('subProcess'): 'Subprocss',
    full_tag('manualTask'): 'Manual Task',
    full_tag('exclusiveGateway'): 'Exclusive Gateway',
    full_tag('parallelGateway'): 'Parallel Gateway',
    full_tag('inclusiveGateway'): 'Inclusive Gateway',
    full_tag('callActivity'): 'Call Activity',
    full_tag('transaction'): 'Transaction',
    full_tag('scriptTask'): 'Script Task',
    full_tag('serviceTask'): 'Service Task',
    full_tag('intermediateCatchEvent'): 'Intermediate Catch Event',
    full_tag('intermediateThrowEvent'): 'Intermediate Throw Event',
    full_tag('boundaryEvent'): 'Boundary Event',
    full_tag('receiveTask'): 'Receive Task',
    full_tag('sendTask'): 'Send Task',
    full_tag('eventBasedGateway'): 'Event Based Gateway',
    full_tag('cancelEventDefinition'): 'Cancel',
    full_tag('errorEventDefinition'): 'Error',
    full_tag('escalationEventDefinition'): 'Escalation',
    full_tag('terminateEventDefinition'): 'Terminate',
    full_tag('messageEventDefinition'): 'Message',
    full_tag('signalEventDefinition'): 'Signal',
    full_tag('timerEventDefinition'): 'Timer',
}
