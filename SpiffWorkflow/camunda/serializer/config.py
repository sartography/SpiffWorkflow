from copy import deepcopy

from SpiffWorkflow.bpmn.serializer.workflow import DEFAULT_SPEC_CONFIG
from SpiffWorkflow.bpmn.serializer.task_spec import (
    UserTaskConverter as DefaultUserTaskConverter,
    ParallelMultiInstanceTaskConverter as DefaultParallelMIConverter,
    SequentialMultiInstanceTaskConverter as DefaultSequentialMIConverter,
)
from SpiffWorkflow.bpmn.serializer.event_definition import MessageEventDefinitionConverter as DefaultMessageEventConverter


from .task_spec import UserTaskConverter, ParallelMultiInstanceTaskConverter, SequentialMultiInstanceTaskConverter
from .event_definition import MessageEventDefinitionConverter


CAMUNDA_SPEC_CONFIG = deepcopy(DEFAULT_SPEC_CONFIG)
CAMUNDA_SPEC_CONFIG['task_specs'].remove(DefaultUserTaskConverter)
CAMUNDA_SPEC_CONFIG['task_specs'].append(UserTaskConverter)
CAMUNDA_SPEC_CONFIG['task_specs'].remove(DefaultParallelMIConverter)
CAMUNDA_SPEC_CONFIG['task_specs'].append(ParallelMultiInstanceTaskConverter)
CAMUNDA_SPEC_CONFIG['task_specs'].remove(DefaultSequentialMIConverter)
CAMUNDA_SPEC_CONFIG['task_specs'].append(SequentialMultiInstanceTaskConverter)

CAMUNDA_SPEC_CONFIG['event_definitions'].remove(DefaultMessageEventConverter)
CAMUNDA_SPEC_CONFIG['event_definitions'].append(MessageEventDefinitionConverter)
