from typing import (
    Iterable, List, Any,
    Iterator, Type,
    Callable
)
import os
import json
import shutil
import inspect
import tempfile
from loguru import logger
from hashlib import sha256
from .extra_typing import T
from itertools import islice
from functools import partialmethod
from torch_data_utils.settings import ROOT_DIR

# Constants
CACHE_DIRECTORY = os.path.join(ROOT_DIR, '.torch_data_utils_cache')


def partialclass(cls: Type[T], *args, **kwargs) -> T:
    """
    Just like `partialmethod` from `functools`
    it performs partial init for classes.
    `Args` and `kwargs` are parameters that needs to be fixed
    for class init
    """
    class PartialCls(cls):
        __init__ = partialmethod(cls.__init__, *args, **kwargs)
    return PartialCls


def save_params(func: Callable) -> Callable:
    """
    Decorator to save parameters of function call in class.

    It works only for functions
    that doesn't have `*args` in its arguments list.
    """
    def wrapper(cls: Type[T], *args, **kwargs) -> Any:
        cls.__init_params__ = {
            # Start from one as the first one is self.
            arg: value for arg, value in zip(inspect.getfullargspec(func).args[1:], args)
        }
        cls.__init_params__.update(kwargs)
        return func(cls, *args, **kwargs)
    return wrapper


def lazy_groups_of(iterable: Iterable[List[Any]], group_size: int) -> Iterator[List[List[Any]]]:
    """
    Takes an iterable and batches the individual instances into lists of the
    specified size. The last list may be smaller if there are instances left over.
    """
    iterator = iter(iterable)
    while True:
        s = list(islice(iterator, group_size))
        if len(s) > 0:
            yield s
        else:
            break
