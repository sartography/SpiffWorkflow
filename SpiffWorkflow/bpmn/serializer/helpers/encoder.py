import json
from types import ModuleType


def create_encoder(registry, user_encoder_cls=None):
    base = user_encoder_cls or json.JSONEncoder

    class SpiffEncoder(base):
        def default(self, obj):
            typename = registry.typenames.get(type(obj))
            if typename is not None:
                return registry.convert_to_dict[typename](obj)
            if callable(obj) or isinstance(obj, ModuleType):
                return None
            if isinstance(obj, set):
                return list(obj)
            return super().default(obj)

    return SpiffEncoder
