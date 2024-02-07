Logging
=======

Spiff provides several loggers:
 - the :code:`spiff` logger, which emits messages when a workflow is initialized and when tasks change state
 - the :code:`spiff.metrics` logger, which emits messages containing the elapsed duration of tasks

All log entries created during the course of running a workflow contain the following extra attributes:

- :code:`workflow_spec`: the name of the current workflow spec
- :code:`task_spec`: the name of the task spec
- :code:`task_id`: the ID of the task)
- :code:`task_type`: the name of the task's spec's class

If the log level is less than 20:

- :code:`data` the task data (this can be quite large and is only made available for debugging purposes)

If the log level is less than or equal to 10:

- :code:`internal_data`: the task internal data (only available at DEBUG or below because it is not typically useful)

The metrics logger additionally provides and only emits messages at the DEBUG level:

- :code:`elapsed`: the time it took the task to run after (ie, the duration of the :code:`task.run` method)

In our command line UI (:app:`cli/subcommands.py`), we've added a few of these extra attributes to the log records:

.. code-block:: python

    spiff_logger = logging.getLogger('spiff')
    spiff_handler = logging.StreamHandler()
    spiff_handler.setFormatter('%(asctime)s [%(name)s:%(levelname)s] (%(workflow_spec)s:%(task_spec)s) %(message)s')
    spiff_logger.addHandler(spiff_handler)

    metrics_logger = logging.getLogger('spiff.metrics')
    metrics_handler = logging.StreamHandler()
    metrics_handler.setFormatter('%(asctime)s [%(name)s:%(levelname)s] (%(workflow_spec)s:%(task_spec)s) %(elasped)s')
    metrics_logger.addHandler(metrics_handler)

In the configuration module :app:`spiff/file.py` that appears in many examples, we set the level of the :code:`spiff`
logger to :code:`INFO`, so that we'll see messages about task state changes, but we ignore the metrics log; however,
the configuration could easily be changed to include it (it can, however generate a high volume of very large records,
so consider yourself warned!).

