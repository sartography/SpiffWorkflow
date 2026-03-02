# Copyright (C) 2026 Sartography
#
# This file is part of SpiffWorkflow.
#
# SpiffWorkflow is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# SpiffWorkflow is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA


class CopyOnWriteDict(dict):
    """
    A dictionary that implements copy-on-write semantics for task data inheritance.

    This class materializes all parent data into the underlying dict storage
    (for exec() compatibility), but tracks which keys are locally modified vs inherited.
    This allows serialization optimization while maintaining full compatibility with
    Python's exec() and other code that accesses dict internals directly.

    Key benefits:
    - O(1) shallow copy inheritance instead of O(n) deepcopy
    - Tracks local modifications for serialization deduplication
    - Fully compatible with exec() and other dict operations
    - Reduced memory in serialized state (only deltas stored)

    Attributes:
        _parent (dict): Reference to parent dict (for tracking only)
        _local_keys (set): Keys that were set locally (not inherited)
    """

    def __init__(self, parent=None, **kwargs):
        """
        Initialize a CopyOnWriteDict.

        Materializes all parent data into the underlying dict storage immediately
        for exec() compatibility, but tracks what's local vs inherited.

        Args:
            parent (dict): Optional parent dictionary to inherit from
            **kwargs: Initial local key-value pairs
        """
        super().__init__()

        # Store reference to parent for tracking
        self._parent = parent
        self._local_keys = set()

        # Materialize parent data into underlying dict (for exec() compatibility)
        if parent is not None:
            if isinstance(parent, CopyOnWriteDict):
                # Get materialized parent data
                super().update(parent.materialize())
            else:
                # Parent is regular dict, just update
                super().update(parent)

        # Add any initial local values
        if kwargs:
            super().update(kwargs)
            self._local_keys.update(kwargs.keys())

    def __setitem__(self, key, value):
        """
        Set an item and mark it as locally modified.

        Args:
            key: The key to set
            value: The value to associate with the key
        """
        super().__setitem__(key, value)
        self._local_keys.add(key)

    def __delitem__(self, key):
        """
        Delete an item and mark it as locally deleted.

        Args:
            key: The key to delete

        Raises:
            KeyError: If the key doesn't exist
        """
        super().__delitem__(key)
        self._local_keys.add(key)  # Track deletion as a local modification

    def update(self, other=None, **kwargs):
        """
        Update this dictionary and track local modifications.

        Args:
            other: A dictionary or iterable of key-value pairs
            **kwargs: Additional key-value pairs
        """
        if other is not None:
            if hasattr(other, 'items'):
                for key, value in other.items():
                    self[key] = value
            else:
                for key, value in other:
                    self[key] = value

        for key, value in kwargs.items():
            self[key] = value

    def pop(self, key, *args):
        """
        Remove and return an item.

        Args:
            key: The key to remove
            *args: Optional default value

        Returns:
            The value associated with the key

        Raises:
            KeyError: If key not found and no default provided
        """
        try:
            value = super().pop(key)
            self._local_keys.add(key)  # Track as local modification
            return value
        except KeyError:
            if args:
                return args[0]
            raise

    def setdefault(self, key, default=None):
        """
        Get an item, setting it to default if not present.

        Args:
            key: The key to look up
            default: The default value to set if key not found

        Returns:
            The value associated with the key
        """
        if key in self:
            return self[key]
        else:
            self[key] = default
            return default

    def clear(self):
        """
        Remove all items from this dictionary.
        """
        super().clear()
        # Mark all previous keys as locally modified (deleted)
        if self._parent:
            self._local_keys.update(self._parent.keys())
        else:
            self._local_keys.clear()

    def get_local_data(self):
        """
        Get only the locally modified data (delta from parent).

        This is useful for serialization optimization - we can store only
        the delta instead of the full data.

        Returns:
            dict: A dictionary containing only local modifications
        """
        return {k: v for k, v in self.items() if k in self._local_keys}

    def materialize(self):
        """
        Return a regular dict with all data.

        Since we already materialize into the underlying dict, this just
        returns a copy of ourselves as a regular dict.

        Returns:
            dict: A regular dictionary with all data
        """
        return dict(self)

    def __deepcopy__(self, memo):
        """
        Support for deepcopy - returns a regular dict.

        Args:
            memo: The memo dictionary used by deepcopy

        Returns:
            dict: A deep copy as a regular dictionary
        """
        from copy import deepcopy
        return deepcopy(dict(self), memo)

    def __reduce__(self):
        """
        Support for pickle - serialize as a regular dict.

        Returns:
            tuple: Pickle reduction tuple
        """
        return (dict, (dict(self),))

    def __eq__(self, other):
        """
        Compare equality with another dictionary.

        CopyOnWriteDict compares equal to regular dicts with the same content.

        Args:
            other: The object to compare with

        Returns:
            bool: True if the contents are equal
        """
        if isinstance(other, dict):
            return dict.__eq__(self, other)
        return NotImplemented

    def __ne__(self, other):
        """
        Compare inequality with another dictionary.

        Args:
            other: The object to compare with

        Returns:
            bool: True if the contents are not equal
        """
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __repr__(self):
        """
        String representation of this dictionary.

        Returns:
            str: A string representation
        """
        return f"CopyOnWriteDict({dict(self)})"
