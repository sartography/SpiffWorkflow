from functools import partial

class DictionaryConverter:

    def __init__(self):

        self.convert_to_dict = { }
        self.convert_from_dict = { }
        self.typenames = { }

    def register(self, cls, to_dict, from_dict, typename=None):

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

    @staticmethod
    def obj_from_dict_attrs(cls, dct):
        return cls(**dct)

    def convert(self, obj):

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

        if isinstance(val, dict) and 'typename' in val:
            from_dict = self.convert_from_dict.get(val.pop('typename'))
            return from_dict(val)
        elif isinstance(val, dict):
            return dict((k, self.restore(v)) for k, v in val.items())
        if isinstance(val, (list, tuple, set)):
            return val.__class__([ self.restore(item) for item in val ])
        else:
            return val
