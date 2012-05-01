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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
import logging

from SpiffWorkflow.Task import Task
from SpiffWorkflow.exceptions import WorkflowException
from SpiffWorkflow.specs.TaskSpec import TaskSpec
from SpiffWorkflow.operators import valueof, Attrib

try:
    from celery.execute import send_task
    from celery.result import AsyncResult
    from celery.app import app_or_default
except ImportError:
    print "Unable to import python-celery imports. These are only needed if"\
            " the celery task spec is used"

LOG = logging.getLogger(__name__)


def eval_args(args, my_task):
    """Parses args and evaluates any Attrib entries"""
    results = []
    for arg in args:
        if isinstance(arg, Attrib):
            results.append(valueof(my_task, arg))
        else:
            results.append(arg)
    return results


def eval_kwargs(kwargs, my_task):
    """Parses kwargs and evaluates any Attrib entries"""
    results = {}
    for kwarg, value in kwargs.iteritems():
        if isinstance(value, Attrib):
            results[kwarg] = valueof(my_task, value)
        else:
            results[kwarg] = value
    return results


class Celery(TaskSpec):
    """This class implements a celeryd task that is sent to the celery queue for
    completion."""

    def __init__(self, parent, name, call, call_args=None, result_key=None,
                 **kwargs):
        """Constructor.

        The args/kwargs arguments support Attrib classes in the parameters for
        delayed evaluation of inputs until run-time. Example usage:
        task = Celery(wfspec, 'MyTask', 'celery.call',
                 call_args=['hello', 'world', Attrib('number')],
                 any_param=Attrib('result'))

        For serialization, the celery task_id is stored in internal_attributes,
        but the celery async call is only storred as an attr of the task (since
        it is not always serializable). When deserialized, the async_call attr
        is reset in the try_fire call.

        @type  parent: TaskSpec
        @param parent: A reference to the parent task spec.
        @type  name: str
        @param name: The name of the task spec.
        @type  call: str
        @param call: The name of the celery task that needs to be called.
        @type  call_args: list
        @param call_args: args to pass to celery task.
        @type  result_key: str
        @param result_key: The key to use to store the results of the call in
                task.attributes. Default is the value of 'call'.
        @type  kwargs: dict
        @param kwargs: kwargs to pass to celery task.
        """
        assert parent  is not None
        assert name    is not None
        assert call is not None
        TaskSpec.__init__(self, parent, name, **kwargs)
        self.call = call
        self.args = call_args
        self.kwargs = kwargs
        self.result_key = result_key or call

    def try_fire(self, my_task, force=False):
        """Returns False when successfully fired, True otherwise"""

        # Deserialize async call if necessary
        if not hasattr(my_task, 'async_call') and \
                my_task._get_internal_attribute('task_id') is not None:
            task_id = my_task._get_internal_attribute('task_id')
            my_task.async_call = app_or_default().AsyncResult(task_id)
            LOG.debug("Reanimate AsyncCall %s" % task_id)

        # Make the call if not already done
        if not hasattr(my_task, 'async_call'):
            if self.args:
                args = eval_args(self.args, my_task)
                if self.kwargs:
                    async_call = send_task(self.call, args=args,
                            kwargs=eval_kwargs(self.kwargs, my_task))
                else:
                    async_call = send_task(self.call, args=args)
            else:
                if self.kwargs:
                    async_call = send_task(self.call,
                            kwargs=eval_kwargs(self.kwargs, my_task))
                else:
                    async_call = send_task(self.call)
            my_task._set_internal_attribute(task_id=str(async_call))
            my_task.async_call = async_call
            LOG.debug("'%s' called: %s" % (self.call, my_task.async_call))

        # Get call status (and manually refr4esh if deserialized)
        if my_task.get_attribute("deserialized"):
            my_task.async_call.state  # must manually refresh if deserialized
        if my_task.async_call.ready():
            LOG.debug("Completed celery call %s with result=%s" % (self.call,
                    my_task.async_call.result))
            my_task.set_attribute(**{self.result_key:
                    my_task.async_call.result})
            return True
        else:
            LOG.debug("TryFire for %s returning False" % my_task.get_name())
            return False

    def _update_state_hook(self, my_task):
        if not self.try_fire(my_task):
            LOG.debug("TryFire for %s returned False, so going to WAITING "
                    "state" % my_task.get_name())
            my_task.state = Task.WAITING
            result = False
        else:
            result = super(Celery, self)._update_state_hook(my_task)
        return result

    def serialize(self, serializer):
        return serializer._serialize_celery(self)

    @classmethod
    def deserialize(self, serializer, wf_spec, s_state):
        spec = serializer._deserialize_celery(wf_spec, s_state)
        return spec
