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

from .version_1_1 import move_subprocesses_to_top
from .version_1_2 import (
    convert_timer_expressions,
    add_default_condition_to_cond_task_specs,
    create_data_objects_and_io_specs,
    check_multiinstance,
    remove_loop_reset,
    update_task_states,
    convert_simple_tasks,
    update_bpmn_attributes,
)
from .version_1_3 import (
    update_event_definition_attributes,
    remove_boundary_event_parent,
    remove_root_task,
    add_new_typenames,
    update_data_objects,
)
from .version_1_4 import update_mi_states

def from_version_1_3(dct):
    """Upgrade serialization from v1.3 to v1.4

    Multiinstance tasks now rely on events rather than polling to merge children, so once
    they are reached, they should be STARTED rather than WAITING.
    """
    dct['VERSION'] = "1.3"
    update_mi_states(dct)

def from_version_1_2(dct):
    """Upgrade serialization from v.1.2 to v.1.3

    The internal/external distinction on event definitions was replaced with the ability to
    target a specific workflow.

    Boundary event parent gateway tasks ave been replaced with a gateway structure.

    The creation of an unnecessary root task was removed; the workflow spec's start task is
    used as the root instead.

    BpmnWorkflows and BpmnSubworkflows were split into to classes.

    Data objects are now stored on the topmost workflow where they are defined.
    """
    dct['VERSION'] = "1.3"
    update_event_definition_attributes(dct)
    remove_boundary_event_parent(dct)
    remove_root_task(dct)
    add_new_typenames(dct)
    update_data_objects(dct)

def from_version_1_1(dct):
    """
    Upgrade v1.1 serialization to v1.2.

    Expressions in timer event definitions have been converted from python expressions to 
    ISO 8601 expressions.

    Cycle timers no longer connect back to themselves.  New children are created from a single
    tasks rather than reusing previously executed tasks.

    All conditions (including the default) are included in the conditions for gateways.

    Data inputs and outputs on process specs were moved inside a BPMNIOSpecification, and
    are now TaskDataReferences; BpmnDataSpecifications that referred to Data Objects are
    now DataObjects.

    Multiinstance tasks were completely refactored, in a way that is simply too difficult to
    migrate.

    Loop reset tasks were removed.
    """
    dct['VERSION'] = "1.2"
    convert_timer_expressions(dct)
    add_default_condition_to_cond_task_specs(dct)
    create_data_objects_and_io_specs(dct)
    check_multiinstance(dct)
    remove_loop_reset(dct)
    update_task_states(dct)
    convert_simple_tasks(dct)
    update_bpmn_attributes(dct)
    from_version_1_2(dct)

def from_version_1_0(dct):
    """
    Upgrade v1.0 serializations to v1.1.

    Starting with Spiff 1.1.8, subworkflows are no longer integrated in main task tree.  When
    a subworkflow (a subprocess, transaction, or call activity) is reached, a subprocss is
    added to the top level workflow and the task enters a waiting state until the workflow
    completes.

    To make the serialization backwards compatible, we delete the tasks from the main workflow
    task list and add them to the appropriate subprocess and recreate the remaining subprocess
    attributes based on the task states.
    """
    dct['VERSION'] = "1.1"
    move_subprocesses_to_top(dct)
    from_version_1_1(dct)

MIGRATIONS = {
    '1.0': from_version_1_0,
    '1.1': from_version_1_1,
    '1.2': from_version_1_2,
    '1.3': from_version_1_3,
}
