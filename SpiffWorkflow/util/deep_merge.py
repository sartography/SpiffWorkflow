
class DeepMerge(object):
    # Merges two deeply nested dictionaries, useful for updating things
    # like task data.

    @staticmethod
    def merge(a, b, path=None):
        "merges b into a"
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    DeepMerge.merge(a[key], b[key], path + [str(key)])
                if isinstance(a[key], list) and isinstance(b[key], list):
                    a[key] = list(set().union(a[key], b[key]))
                else:
                    a[key] = b[key]
            else:
                a[key] = b[key]
        return a

