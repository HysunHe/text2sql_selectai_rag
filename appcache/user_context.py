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
from typing import Optional, Dict

__USER_CONTEXT__ = {}


def set_entry(
    user: str,
    entry_name: str,
    entry_value,
    additional_attributes: Optional[Dict] = None,
):
    __USER_CONTEXT__[f"{user}_{entry_name}"] = {
        "val": entry_value,
        "ts": time.time(),
        "attrs": additional_attributes,
    }


def set_entry_attr(user: str, entry_name: str, attr_name: str, attr_val: str) -> any:
    if f"{user}_{entry_name}" not in __USER_CONTEXT__:
        set_entry(user=user, entry_name=entry_name, entry_value=None)
    attrs = __USER_CONTEXT__[f"{user}_{entry_name}"]["attrs"]
    if attrs is None:
        attrs = {}
        __USER_CONTEXT__[f"{user}_{entry_name}"]["attrs"] = attrs
    attrs[attr_name] = attr_val


def get_entry(user: str, entry_name: str) -> any:
    if f"{user}_{entry_name}" not in __USER_CONTEXT__:
        return None
    return __USER_CONTEXT__[f"{user}_{entry_name}"]


def get_entry_val(user: str, entry_name: str) -> any:
    if f"{user}_{entry_name}" not in __USER_CONTEXT__:
        return None
    return __USER_CONTEXT__[f"{user}_{entry_name}"]["val"]


def get_entry_attr(user: str, entry_name: str, attr_name: str) -> any:
    if f"{user}_{entry_name}" not in __USER_CONTEXT__:
        return None
    attrs = __USER_CONTEXT__[f"{user}_{entry_name}"]["attrs"]
    return attrs[attr_name] if attrs and attr_name in attrs else None


def remove_entry(user: str, entry_name: str) -> None:
    del __USER_CONTEXT__[f"{user}_{entry_name}"]


def exists_entry(user: str, entry_name: str):
    return True if f"{user}_{entry_name}" in __USER_CONTEXT__ else False


def is_entry_empty(user: str, entry_name: str):
    val = get_entry_val(user, entry_name)
    return val == None or str(val).strip() in ("", "unspecified", "未指定")


def clear_all():
    for k in __USER_CONTEXT__.keys():
        del __USER_CONTEXT__[k]


def clear(user: str):
    for k in __USER_CONTEXT__.keys():
        if str(k).startswith(user):
            del __USER_CONTEXT__[k]
