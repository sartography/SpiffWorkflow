import logging
import time

from SpiffWorkflow import Task

LOG = logging.getLogger(__name__)

def firsttime():
    return time.time()

def sincetime(txt,lasttime):
    thistime=firsttime()
    LOG.info('%2.4f | %s' % (thistime-lasttime, txt))
    return thistime


def timeit(f):

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        arguments = []
        task = ""
        task_type = ""
        for arg in args:
            if isinstance(arg, Task):
                task = arg.get_description()
                task_type = arg.task_spec.__class__.__name__
            if isinstance(arg, str):
                argument = arg[:75] + '..' if len(arg) > 75 else arg
                arguments.append(argument.replace("\n", " "))
            else:
                arguments.append(arg.__class__.__name__)

        LOG.info('| %2.4f | % s | %s | %r  | %s ' % (te-ts, task, task_type, f.__name__, " | ".join(arguments)))
        return result

    return timed
