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

from SpiffWorkflow.bpmn.specs.MultiInstanceTask import (
    StandardLoopTask as BpmnStandardLoopTask,
    ParallelMultiInstanceTask as BpmnParallelMITask,
    SequentialMultiInstanceTask as BpmnSequentialMITask,
)
from .spiff_task import SpiffBpmnTask

class StandardLoopTask(BpmnStandardLoopTask, SpiffBpmnTask):
    pass

class ParallelMultiInstanceTask(BpmnParallelMITask, SpiffBpmnTask):
    pass

class SequentialMultiInstanceTask(BpmnSequentialMITask, SpiffBpmnTask):
    pass