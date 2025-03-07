""" 
Description: 
 - AiReport project. This is a demo POC project, it is not intented
   for production. The quality of the code is not guaranteed. 
   
   If you refrence the code in this project, it means that you understand
   the risk and you are responsible for any issues caused by the code.

History:
 - 2025/01/20 by Hysun (hysun.he@oracle.com): Initial implementation.
"""

import time
import logging

_logger = logging.getLogger(__name__)

__RESULT_CACHE__ = {}


def set_entry(entry_name: str, entry_value):
    if not entry_value:
        remove_entry(entry_name)
    else:
        __RESULT_CACHE__[entry_name] = {
            "val": entry_value,
            "ts": time.time(),
        }


def set_entries(entry_name: list[str] | str, entry_value):
    if isinstance(entry_name, str):
        set_entry(entry_name, entry_value)
    else:
        for name in entry_name:
            set_entry(name, entry_value)


def get_entry(entry_name: str) -> any:
    if entry_name not in __RESULT_CACHE__:
        return None
    return __RESULT_CACHE__[entry_name]["val"]


def remove_entry(entry_name: str) -> None:
    del __RESULT_CACHE__[entry_name]


def exists_entry(entry_name: str):
    return True if entry_name in __RESULT_CACHE__ else False


def clear_all():
    for k in __RESULT_CACHE__.keys():
        del __RESULT_CACHE__[k]


def clear(prefix: str):
    for k in __RESULT_CACHE__.keys():
        if str(k).startswith(prefix):
            del __RESULT_CACHE__[k]


def print_debug():
    for k in __RESULT_CACHE__.keys():
        _logger.debug(f"k: {k}, v: {__RESULT_CACHE__[k]}")
