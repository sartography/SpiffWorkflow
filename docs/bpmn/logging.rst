Logging
=======

Spiff provides several loggers:

 - the :code:`spiff.workflow` logger, which emits messages when actions are taken on a workflow
 - the :code:`spiff.task` logger, which emits messages when tasks change state

Records emitted at the :code:`INFO` level, with addtional attributes available for debugging if the level is lower.

Log entries emitted by the :code:`spiff.workflow` logger contain the following extra atributes:

- :code:`workflow_spec`: the name of the spec for this workflow
- :code:`completed`: whether the workflow has completed
- :code:`success`: the value of the :code:`success` attribute

If the log level is less than 20, records include the following extra attribute:

- :code:`tasks`: a list of the task ids in the workflow

Log entries emitted by the :code:`spiff.task` logger contain the following extra attributes:

- :code:`workflow_spec`: the name of the spec for this workflow
- :code:`task_spec`: the name of the spec for this task
- :code:`task_id`: the ID of the task)
- :code:`task_type`: the name of the task's spec's class
- :code:`state`: the name of the tasks :code:`TaskState`
- :code:`last_state_chsnge`: the timestamp at which the state change was made
- :code:`elapsed`: the elapsed time since the previous state transition
- :code:`parent`: the id of the task's parent

If the log level is less than 20, records include the following extra attributes:

- :code:`data` the task data
- :code:`internal_data`: the task internal data

Log entries containing task data and internal data can be quite large, so use with caution!

In our command line UI (:app:`cli/subcommands.py`), we've added a few of these extra attributes to the log records:

.. code-block:: python

    task_logger = logging.getLogger('spiff.task')
    task_handler = logging.StreamHandler()
    task_handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s:%(levelname)s] (%(workflow_spec)s:%(task_spec)s) %(message)s'))
    task_logger.addHandler(task_handler)

    wf_logger = logging.getLogger('spiff.workflow')
    wf_handler = logging.StreamHandler()
    wf_handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s:%(levelname)s] (%(workflow_spec)s) %(message)s'))
    wf_logger.addHandler(wf_handler)
