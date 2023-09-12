# Copyright (C) 2023 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

from copy import deepcopy

from SpiffWorkflow.bpmn.serializer.workflow import DEFAULT_SPEC_CONFIG
from SpiffWorkflow.bpmn.serializer.default.task_spec import (
    UserTaskConverter as DefaultUserTaskConverter,
    ParallelMultiInstanceTaskConverter as DefaultParallelMIConverter,
    SequentialMultiInstanceTaskConverter as DefaultSequentialMIConverter,
)
from SpiffWorkflow.bpmn.serializer.default.event_definition import MessageEventDefinitionConverter as DefaultMessageEventConverter

from .task_spec import (
    UserTaskConverter,
    BusinessRuleTaskConverter,
    ParallelMultiInstanceTaskConverter,
    SequentialMultiInstanceTaskConverter
)
from .event_definition import MessageEventDefinitionConverter


CAMUNDA_SPEC_CONFIG = deepcopy(DEFAULT_SPEC_CONFIG)
CAMUNDA_SPEC_CONFIG['task_specs'].remove(DefaultUserTaskConverter)
CAMUNDA_SPEC_CONFIG['task_specs'].append(UserTaskConverter)
CAMUNDA_SPEC_CONFIG['task_specs'].remove(DefaultParallelMIConverter)
CAMUNDA_SPEC_CONFIG['task_specs'].append(ParallelMultiInstanceTaskConverter)
CAMUNDA_SPEC_CONFIG['task_specs'].remove(DefaultSequentialMIConverter)
CAMUNDA_SPEC_CONFIG['task_specs'].append(SequentialMultiInstanceTaskConverter)
CAMUNDA_SPEC_CONFIG['task_specs'].append(BusinessRuleTaskConverter)

CAMUNDA_SPEC_CONFIG['event_definitions'].remove(DefaultMessageEventConverter)
CAMUNDA_SPEC_CONFIG['event_definitions'].append(MessageEventDefinitionConverter)
