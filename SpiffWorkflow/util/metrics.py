import logging
import time

LOG = logging.getLogger(__name__)
threshold = 0.01


def firsttime():
    return time.time()

def sincetime(txt,lasttime):
    thistime=firsttime()
    if thistime - lasttime > threshold:
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

            if arg.__class__.__name__ == 'Task' and arg.__class__.__module__.startswith('SpiffWorkflow'):
                task = arg.get_description()
                task_type = arg.task_spec.__class__.__name__
            if isinstance(arg, str):
                argument = arg[:75] + '..' if len(arg) > 75 else arg
                arguments.append(argument.replace("\n", " "))
            else:
                arguments.append(arg.__class__.__name__)
        if te-ts > threshold:
            LOG.info('| %2.4f | % s | %s | %r  | %s  ' % (te-ts, f.__qualname__, task, task_type, " | ".join(arguments)))
        return result

    return timed
