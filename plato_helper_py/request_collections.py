from collections import UserDict
from typing import Any


class RequestDict(UserDict):
    """
    Dictionary to be used with the requests' library.
    Does not take None entries, deletes keys that get updated to None and works recursively.

    >>> RequestDict({"a": 2, "b": None, "c": {"d": None}})
    {'a': 2, 'c': {}}
    >>> dict_ = RequestDict({"a": 2})
    >>> dict_["a"] = None
    >>> dict_
    {}
    """
    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set the value of the dictionary

        :param key: The key to set
        :type key: Any

        :param value: The value to set
        :type value: Any
        """
        if value is not None:
            if isinstance(value, dict):
                value = RequestDict(value)
            return super().__setitem__(key, value)
        if super().__contains__(key):
            return super().__delitem__(key)
        return None
