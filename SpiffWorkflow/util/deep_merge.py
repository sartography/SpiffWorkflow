class DeepMerge(object):
    # Merges two deeply nested json-like dictionaries,
    # useful for updating things like task data.
    # I know in my heart, that this isn't completely correct.
    # But I don't want to create a dependency, and this is passing
    # all the failure points I've found so far.  So I'll just
    # keep plugging away at it.
    # This will merge all updates from b into a, but it does not
    # remove items from a that are not in b.  Passing a prune of
    # true, and it WILL remove items in a that are not in b.

    @staticmethod
    def merge(a, b, path=None):
        "merges b into a"
        if path is None: path = []
        for key in b:
            if key in a:
                if a[key] == b[key]:
                    continue
                elif isinstance(a[key], dict) and isinstance(b[key], dict):
                    DeepMerge.merge(a[key], b[key], path + [str(key)])
                elif isinstance(a[key], list) and isinstance(b[key], list):
                    DeepMerge.merge_array(a[key], b[key], path + [str(key)])
                else:
                    a[key] = b[key]  # Just overwrite the value in a.
            else:
                a[key] = b[key]
        return a

    @staticmethod
    def merge_array(a, b, path=None):

        for idx, val in enumerate(b):
            if isinstance(b[idx], dict):  # Recurse back on dictionaries.
                # If lists of dictionaries get out of order, this might
                # cause us some pain.
                if len(a) > idx:
                    a[idx] = DeepMerge.merge(a[idx], b[idx], path + [str(idx)])
                else:
                    a.append(b[idx])
            else: # Just merge whatever it is back in.
                a.extend(x for x in b if x not in a)

        # Trim a back to the length of b.  In the end, the two arrays should match
        del a[len(b):]
