import copy

class BasePythonScriptEngineEnvironment:
    def __init__(self, environment_globals):
        self.globals = environment_globals

    def evaluate(self, expression, context, external_methods=None):
        raise NotImplementedError("Subclass must implement this method")

    def execute(self, script, context, external_methods=None):
        raise NotImplementedError("Subclass must implement this method")

class Box(dict):
    """
    Example:
    m = Box({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(Box, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        self[k] = Box(v)
                    else:
                        self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    self[k] = Box(v)
                else:
                    self[k] = v

    def __deepcopy__(self, memodict=None):
        if memodict is None:
            memodict = {}
        my_copy = Box()
        for k, v in self.items():
            my_copy[k] = copy.deepcopy(v)
        return my_copy

    def __getattr__(self, attr):
        try:
            output = self[attr]
        except:
            raise AttributeError(
                "Dictionary has no attribute '%s' " % str(attr))
        return output

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Box, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__init__(state)

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Box, self).__delitem__(key)
        del self.__dict__[key]

    @classmethod
    def convert_to_box(cls, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if not isinstance(value, Box):
                    data[key] = cls.convert_to_box(value)
            return Box(data)
        if isinstance(data, list):
            for idx, value in enumerate(data):
                data[idx] = cls.convert_to_box(value)
            return data
        return data

class TaskDataEnvironment(BasePythonScriptEngineEnvironment):
    def evaluate(self, expression, context, external_methods=None):
        my_globals = copy.copy(self.globals)  # else we pollute all later evals.
        Box.convert_to_box(context)
        my_globals.update(external_methods or {})
        my_globals.update(context)
        return eval(expression, my_globals)

    def execute(self, script, context, external_methods=None):
        my_globals = copy.copy(self.globals)
        Box.convert_to_box(context)
        my_globals.update(external_methods or {})
        context.update(my_globals)
        try:
            exec(script, context)
        finally:
            self._remove_globals_and_functions_from_context(context, external_methods)

    def _remove_globals_and_functions_from_context(self, context,
                                                  external_methods=None):
        """When executing a script, don't leave the globals, functions
        and external methods in the context that we have modified."""
        for k in list(context):
            if k == "__builtins__" or \
                    hasattr(context[k], '__call__') or \
                    k in self.globals or \
                    external_methods and k in external_methods:
                context.pop(k)
