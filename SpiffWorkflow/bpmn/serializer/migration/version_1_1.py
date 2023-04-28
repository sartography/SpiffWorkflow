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

def move_subprocesses_to_top(dct):
    subprocesses = dict((sp, { 'tasks': {}, 'root': None, 'data': {}, 'success': True }) for sp in dct['subprocesses'])

    # Move the tasks out of the top-level
    for sp, task_ids in dct['subprocesses'].items():
        for task_id in task_ids:
            if task_id in dct['tasks']:
                subprocesses[sp]['tasks'][task_id] = dct['tasks'].pop(task_id)
            if subprocesses[sp]['root'] is None:
                subprocesses[sp]['root'] = task_id
                subprocesses[sp]['tasks'][task_id]['parent'] = None

    # Fix up th task and workflow states
    waiting = []
    for sp in subprocesses:
        completed = sorted(
            [t for t in subprocesses[sp]['tasks'].values() if t['state'] in [32, 64] ],
            key=lambda t: t['last_state_change']
        )
        if len(completed) > 0:
            subprocesses[sp]['last_task'] = completed[-1]
        # If there are uncompleted tasks, set the subworkflow task state to waiting
        if len(completed) < len(subprocesses[sp]['tasks']):
            waiting.append(sp)

    # Check the top level and all subprocesses for waiting tasks
    # Also remove any children that are no longer in the tree
    for sp in [dct] + list(subprocesses.values()):
        for task_id, task in sp['tasks'].items():
            if task_id in waiting:
                task['state'] = 8
            task['children'] = [ c for c in task['children'] if c in sp['tasks'] ]

    dct['subprocesses'] = subprocesses
