# -*- coding: utf-8 -*-

# Copyright (C) 2007 Samuel Abels
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA
import logging
import json

from ..task import Task
from ..exceptions import WorkflowException
from .base import TaskSpec
from ..operators import valueof, Attrib, PathAttrib
from ..util import merge_dictionary

try:
    from celery.app import default_app
except ImportError:
    have_celery = False
else:
    have_celery = True

LOG = logging.getLogger(__name__)


def _eval_args(args, my_task):
    """Parses args and evaluates any Attrib entries"""
    results = []
    for arg in args:
        if isinstance(arg, Attrib) or isinstance(arg, PathAttrib):
            results.append(valueof(my_task, arg))
        else:
            results.append(arg)
    return results


def _eval_kwargs(kwargs, my_task):
    """Parses kwargs and evaluates any Attrib entries"""
    results = {}
    for kwarg, value in list(kwargs.items()):
        if isinstance(value, Attrib) or isinstance(value, PathAttrib):
            results[kwarg] = valueof(my_task, value)
        else:
            results[kwarg] = value
    return results


def Serializable(o):
    """Make sure an object is JSON-serializable
    Use this to return errors and other info that does not need to be
    deserialized or does not contain important app data. Best for returning
    error info and such"""
    if isinstance(o, (str, dict, int)):
        return o
    else:
        try:
            json.dumps(o)
            return o
        except Exception:
            LOG.debug("Got a non-serilizeable object: %s" % o)
            return o.__repr__()


class Celery(TaskSpec):

    """This class implements a celeryd task that is sent to the celery queue for
    completion."""

    def __init__(self, wf_spec, name, call, call_args=None, result_key=None,
                 merge_results=False, **kwargs):
        """Constructor.

        The args/kwargs arguments support Attrib classes in the parameters for
        delayed evaluation of inputs until run-time. Example usage:
        task = Celery(wfspec, 'MyTask', 'celery.call',
                 call_args=['hello', 'world', Attrib('number')],
                 any_param=Attrib('result'))

        For serialization, the celery task_id is stored in internal_data,
        but the celery async call is only stored as an attr of the task (since
        it is not always serializable). When deserialized, the async_call attr
        is reset in the _start call.

        :type  wf_spec: WorkflowSpec
        :param wf_spec: A reference to the workflow specification.
        :type  name: str
        :param name: The name of the task spec.
        :type  call: str
        :param call: The name of the celery task that needs to be called.
        :type  call_args: list
        :param call_args: args to pass to celery task.
        :type  result_key: str
        :param result_key: The key to use to store the results of the call in
                task.internal_data. If None, then dicts are expanded into
                internal_data and values are stored in 'result'.
        :type  merge_results: bool
        :param merge_results: merge the results in instead of overwriting
          existing fields.
        :type  kwargs: dict
        :param kwargs: kwargs to pass to celery task.
        """
        if not have_celery:
            raise Exception("Unable to import python-celery imports.")
        assert wf_spec is not None
        assert name is not None
        assert call is not None
        TaskSpec.__init__(self, wf_spec, name, **kwargs)
        self.description = kwargs.pop('description', '')
        self.call = call or []
        self.args = call_args or {}
        self.merge_results = merge_results
        skip = 'data', 'defines', 'pre_assign', 'post_assign', 'lock'
        self.kwargs = dict(i for i in list(kwargs.items()) if i[0] not in skip)
        self.result_key = result_key
        LOG.debug("Celery task '%s' created to call '%s'" % (name, call))

    def _send_call(self, my_task):
        """Sends Celery asynchronous call and stores async call information for
        retrieval laster"""
        args, kwargs = None, None
        if self.args:
            args = _eval_args(self.args, my_task)
        if self.kwargs:
            kwargs = _eval_kwargs(self.kwargs, my_task)
        LOG.debug(
            "%s (task id %s) calling %s" % (self.name, my_task.id, self.call),
            extra=dict(data=dict(args=args, kwargs=kwargs)))
        async_call = default_app.send_task(self.call, args=args, kwargs=kwargs)
        my_task._set_internal_data(task_id=async_call.task_id)
        my_task.async_call = async_call
        LOG.debug("'%s' called: %s" % (self.call, my_task.async_call.task_id))

    def _restart(self, my_task):
        """ Abort celery task and retry it"""
        if not my_task._has_state(Task.WAITING):
            raise WorkflowException(my_task, "Cannot refire a task that is not"
                                    "in WAITING state")
        # Check state of existing call and abort it (save history)
        if my_task._get_internal_data('task_id') is not None:
            if not hasattr(my_task, 'async_call'):
                task_id = my_task._get_internal_data('task_id')
                my_task.async_call = default_app.AsyncResult(task_id)
                my_task.deserialized = True
                my_task.async_call.state  # manually refresh
            async_call = my_task.async_call
            if async_call.state == 'FAILED':
                pass
            elif async_call.state in ['RETRY', 'PENDING', 'STARTED']:
                async_call.revoke()
                LOG.info("Celery task '%s' was in %s state and was revoked" % (
                    async_call.state, async_call))
            elif async_call.state == 'SUCCESS':
                LOG.warning("Celery task '%s' succeeded, but a refire was "
                            "requested" % async_call)
            self._clear_celery_task_data(my_task)
        # Retrigger
        return self._start(my_task)

    def _clear_celery_task_data(self, my_task):
        """ Clear celery task data """
        # Save history
        if 'task_id' in my_task.internal_data:
            # Save history for diagnostics/forensics
            history = my_task._get_internal_data('task_history', [])
            history.append(my_task._get_internal_data('task_id'))
            del my_task.internal_data['task_id']
            my_task._set_internal_data(task_history=history)
        if 'task_state' in my_task.internal_data:
            del my_task.internal_data['task_state']
        if 'error' in my_task.internal_data:
            del my_task.internal_data['error']
        if hasattr(my_task, 'async_call'):
            delattr(my_task, 'async_call')
        if hasattr(my_task, 'deserialized'):
            delattr(my_task, 'deserialized')

    def _start(self, my_task, force=False):
        """Returns False when successfully fired, True otherwise"""

        # Deserialize async call if necessary
        if not hasattr(my_task, 'async_call') and \
                my_task._get_internal_data('task_id') is not None:
            task_id = my_task._get_internal_data('task_id')
            my_task.async_call = default_app.AsyncResult(task_id)
            my_task.deserialized = True
            LOG.debug("Reanimate AsyncCall %s" % task_id)

        # Make the call if not already done
        if not hasattr(my_task, 'async_call'):
            self._send_call(my_task)

        # Get call status (and manually refresh if deserialized)
        if getattr(my_task, "deserialized", False):
            my_task.async_call.state  # must manually refresh if deserialized
        if my_task.async_call.state == 'FAILURE':
            LOG.debug("Async Call for task '%s' failed: %s" % (
                my_task.get_name(), my_task.async_call.info))
            info = {}
            info['traceback'] = my_task.async_call.traceback
            info['info'] = Serializable(my_task.async_call.info)
            info['state'] = my_task.async_call.state
            my_task._set_internal_data(task_state=info)
        elif my_task.async_call.state == 'RETRY':
            info = {}
            info['traceback'] = my_task.async_call.traceback
            info['info'] = Serializable(my_task.async_call.info)
            info['state'] = my_task.async_call.state
            my_task._set_internal_data(task_state=info)
        elif my_task.async_call.ready():
            result = my_task.async_call.result
            if isinstance(result, Exception):
                LOG.warn("Celery call %s failed: %s" % (self.call, result))
                my_task._set_internal_data(error=Serializable(result))
                return False
            LOG.debug("Completed celery call %s with result=%s" % (self.call,
                                                                   result))
            # Format result
            if self.result_key:
                data = {self.result_key: result}
            else:
                if isinstance(result, dict):
                    data = result
                else:
                    data = {'result': result}
            # Load formatted result into internal_data
            if self.merge_results:
                merge_dictionary(my_task.internal_data, data)
            else:
                my_task.set_data(**data)
            return True
        else:
            LOG.debug("async_call.ready()=%s. TryFire for '%s' "
                      "returning False" % (my_task.async_call.ready(),
                                           my_task.get_name()))
            return False

    def _update_hook(self, my_task):
        if not self._start(my_task):
            if not my_task._has_state(Task.WAITING):
                LOG.debug("'%s' going to WAITING state" % my_task.get_name())
                my_task._set_state(Task.WAITING)
            return
        super(Celery, self)._update_hook(my_task)

    def serialize(self, serializer):
        return serializer.serialize_celery(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        spec = serializer.deserialize_celery(wf_spec, s_state)
        return spec
