import importlib
import logging
from copy import deepcopy, copy

from SpiffWorkflow.bpmn.PythonScriptEngine import PythonScriptEngine
from SpiffWorkflow.task import Task
from SpiffWorkflow.exceptions import WorkflowTaskExecException
from SpiffWorkflow.operators import Operator


class FunctionScriptEngine(PythonScriptEngine):
    LOGGER = logging.getLogger(__name__)

    def __init__(self, pythonpackage=None, before_eval=None,
                 before_execute=None, after_execute=None):
        """
        This class is a secure implementation of PythonScriptEngine. It only allows known modules from a
        specific location (pythonpackage) within the source tree. Also it provides the possibility to do
        pre- and postprocessing.

        Also it passes the taskdata and other (config) parameters as defined in Camunda modeler to the modules thereby
        providing a possibility to use SpiffWorkflow in more complicated systems.

        Evaluate is checked by ast.parse in the original PythonScriptEngine, thus is reasonable safe

        :param pythonpackage: package where modules can be found
        :param before_eval: callable to execute before the eval is executed used to manipulate input data
        :param before_execute: callable to execute before the execute
        :param after_execute: callable to execute after the execute
        """
        self.before_execute = before_execute
        self.after_execute = after_execute
        self.before_eval = before_eval
        self.err = None
        self.pythonpackage = pythonpackage
        super().__init__()

    def evaluate(self, task: Task, expression: str):
        """
        Evaluate the given expression, within the context of the given task and
        return the result.

        Preprocessing allows for more userfriendly input by the user by modifying the locals
        """
        lcls = {}
        if self.before_eval and callable(self.before_eval):
            lcls = self.before_eval(task, expression)

        try:
            if isinstance(expression, Operator):
                # I am assuming that this takes care of some kind of XML
                # expression judging from the contents of operators.py
                return expression._matches(task)
            else:
                return self._evaluate(expression, **task.data,
                                      external_methods=lcls)
        except Exception as e:
            raise WorkflowTaskExecException(task,
                                            "Error evaluating expression "
                                            "'%s', %s" % (expression, str(e)))

    def execute(self, task: Task, script: str, data, external_methods=None):
        """
        The routine receives the name of the script as entered in Camunda. It looks for the function
        and executes it and optionally executes some pre- and postprocessing.

        This routine only executes importable routines. This means that the module needs to be present in the
        Pythonpath. Within the sourcetree it is possible to specify the location of modules by defining
        self.pythonpackage which means that this does not need to be entered by the user.

        If the user enters a single functionname, then it will search for a module with the same name. If not found
        and self.pythonpackage is specified, this is prepended and it will also search that path.

        No parameters are to be entered by the user. The routine is always called by passing the task.data

        :param task:
        :param script:
        :param data:
        :param external_methods:
        :return:
        """
        modulename, functionname = self.get_module_function(script)
        mod_function = self.get_module(modulename, functionname,
                                       self.pythonpackage)

        extensions_parameters = self.bld_extensions_parms(task)

        if self.before_execute and callable(self.before_execute):
            parms = self.before_execute(task, script, extensions_parameters,
                                        self.pythonpackage)
        else:
            taskdata = {'taskdata': deepcopy(task.data)}
            workflowdata = {'workflowdata': deepcopy(task.workflow.data)}
            parms = {**taskdata, **workflowdata,
                     **extensions_parameters}  # I do not want to pollute the originals
        result = None
        # noinspection PyBroadException
        try:
            result = mod_function(**parms)  # All parameters are passed to the function
        except Exception as err:
            self.err = err
        self.auto_update(parms, task)

        if self.after_execute and callable(self.after_execute):
            self.after_execute(result, task, script, self.err)
        elif self.err:
            raise self.err

    @staticmethod
    def auto_update(parms, task):
        """
        Updates scalar params in task.data and task.workflow.data

        :param parms:
        :param task:
        :return:
        """
        for k, v in parms.items():
            if k == 'extensions':
                continue

            if k == 'taskdata':
                task.update_data(parms[k])
            elif k == 'workflowdata':
                task.workflow.data.update(parms[k])
            elif k in task.workflow.data and task.workflow.data[k] != v:
                task.workflow.data[k] = v
            elif k in task.data and task.data[k] != v:
                task.update_data({k: v})
            else:
                task.update_data({k: v})

    @staticmethod
    def bld_extensions_parms(task) -> dict:
        """
        Routine builds a copy of the config parameters read from Camunda and prepares them for passing to the module
        Note that these parameters are read-only (therefor they are copied from the task_spec)

        :param task:
        :return: dict with configuration values
        """
        config = copy(task.task_spec.extensions)
        if len(config):
            return {'extensions': config}
        else:
            return {}

    @staticmethod
    def get_module_function(script):
        """
        Retrieve module and function from entered script. If the script is
        a single term the modulename is the functionname.

        :param script:
        :return:
        """
        if '\n' in script:
            raise PermissionError('script should not contain a linebreak')
        script = script.replace('\r', '').replace('\t', '').strip()
        split_import = script.split('.')
        if len(split_import) == 1:
            modulename = script
            functionname = script
        else:
            modulename = '.'.join(split_import[:-1])
            functionname = split_import[-1]
        return modulename, functionname

    @staticmethod
    def get_module(modulename, functionname, pythonpackage):
        """
        Returns the function as imported if found either directly from the entered modulename or by prefixing the
        pythonpackage.

        If the module does not exist, an ImportError is raised. If the function does not exist in the module
        an AttributeError is raised by Python. Effectively meaning that only functions in a module known to the
        system can be executed.

        :param modulename:  Python module containing the function
        :param functionname: Name of the function to be executed
        :param pythonpackage: Name of the pythonpackage where the module can be found if not specified in Camunda
        :return:
        """
        possiblemodulenames = [modulename, pythonpackage,
                               pythonpackage + '.' + modulename]
        for module in possiblemodulenames:
            try:
                imported = importlib.import_module(module)
            except ImportError:
                continue
            return getattr(imported, functionname)
        raise ImportError(
            'module %s could not be found' % ' or '.join(possiblemodulenames))
