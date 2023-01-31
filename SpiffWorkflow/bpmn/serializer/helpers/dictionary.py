from functools import partial

class DictionaryConverter:
    """
    This is a base class used to convert BPMN specs, workflows, tasks, and data to
    dictionaries of JSON-serializable objects.  Actual serialization is done as the
    very last step by other classes.

    This class allows you to register to_dict and from_dict functions for non-JSON-
    serializable objects.

    When an object is passed into `convert`, it will call the supplied to_dict
    function on any classes that have been registered.  The supplied to_dict function
    must return a dictionary.  The object's `typename` will be added to this dictionary
    by the converter.

    The (unqualified) class name will be used as the `typename` if one is not supplied.
    You can optionally supply our own names (you'll need to do this if you need to 
    identically named classes in multiple packages).

    When a dictionary is passed into `restore`, it will be checked for a `typename` key.
    If a registered `typename` is found, the supplied from_dict function will be 
    called.  Unrecognized objects will be returned as-is.

    For a simple example of how to use this class, see the `BpmnDataConverter` in
    `bpmn_converters`.
    """

    def __init__(self):
        self.convert_to_dict = { }
        self.convert_from_dict = { }
        self.typenames = { }

    def register(self, cls, to_dict, from_dict, typename=None):
        """Register a conversion/restoration.

        The `to_dict` function must return a dictionary; if no `typename` is given,
        the unquallified class name will be used.

        :param cls: the class that will be converted/restored
        :param to_dict: a function that will be called with the object as an argument
        :param from_dict: a function that restores the object from the dict
        :param typename: an optional typename for identifying the converted object
        """
        typename = cls.__name__ if typename is None else typename
        self.typenames[cls] = typename
        self.convert_to_dict[typename] = partial(self.obj_to_dict, typename, to_dict)
        self.convert_from_dict[typename] = partial(self.obj_from_dict, from_dict)

    @staticmethod
    def obj_to_dict(typename, func, obj):
        dct = func(obj)
        dct.update({'typename': typename})
        return dct

    @staticmethod
    def obj_from_dict(func, dct):
        return func(dct)

    def convert(self, obj):
        """
        This is the public conversion method.  It will be applied to dictionary
        values, list items, and the object itself, applying the to_dict functions
        of any registered type to the objects, or return the object unchanged if
        it is not recognized.

        :param obj: the object to be converter

        Returns:
            the dictionary representation for registered objects or the original
            for unregistered objects
        """
        typename = self.typenames.get(obj.__class__)
        if typename in self.convert_to_dict:
            to_dict = self.convert_to_dict.get(typename)
            return to_dict(obj)
        elif isinstance(obj, dict):
            return dict((k, self.convert(v)) for k, v in obj.items())
        elif isinstance(obj, (list, tuple, set)):
            return obj.__class__([ self.convert(item) for item in obj ])
        else:
            return obj

    def restore(self, val):
        """
        This is the public restoration method.  It will be applied to dictionary
        values, list items, and the value itself, checking for a `typename` key and
        applying the from_dict function of any registered type, or return the value
        unchanged if it is not recognized.

        :param val: the value to be converted

        Returns:
            the restored object for registered objects or the original for
            unregistered values
        """
        if isinstance(val, dict) and 'typename' in val:
            from_dict = self.convert_from_dict.get(val.pop('typename'))
            return from_dict(val)
        elif isinstance(val, dict):
            return dict((k, self.restore(v)) for k, v in val.items())
        if isinstance(val, (list, tuple, set)):
            return val.__class__([ self.restore(item) for item in val ])
        else:
            return val
