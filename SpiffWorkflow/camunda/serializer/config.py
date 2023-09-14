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

from SpiffWorkflow.bpmn.serializer.workflow import DEFAULT_CONFIG
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


CAMUNDA_CONFIG = deepcopy(DEFAULT_CONFIG)
CAMUNDA_CONFIG.remove(DefaultUserTaskConverter)
CAMUNDA_CONFIG.append(UserTaskConverter)
CAMUNDA_CONFIG.remove(DefaultParallelMIConverter)
CAMUNDA_CONFIG.append(ParallelMultiInstanceTaskConverter)
CAMUNDA_CONFIG.remove(DefaultSequentialMIConverter)
CAMUNDA_CONFIG.append(SequentialMultiInstanceTaskConverter)
CAMUNDA_CONFIG.append(BusinessRuleTaskConverter)

CAMUNDA_CONFIG.remove(DefaultMessageEventConverter)
CAMUNDA_CONFIG.append(MessageEventDefinitionConverter)
