""" 
Description: 
 - Utility for selectai. This util execute selectai SQL directly,
   for example:
   select ai runsql 'show me all products'

History:
 - 2025/01/20 by Hysun (hysun.he@oracle.com): Initial version
"""

import re
import logging
from dao.db_pool import selectai_pool
from conf import app_config
from oracledb import Cursor
from oracledb import DatabaseError
from typing import List, Optional

_logger = logging.getLogger(__name__)


def runsql_adb(
    user: Optional[str], sentence: str, llm_profile: str
) -> tuple[Optional[List[any]], Optional[List[any]], Optional[List[str]]]:
    result_array = []
    raw_data = []
    header_data = []
    _logger.debug(f"Running SelectAI in runtime mode ...[{llm_profile}]")
    sql = f"select ai runsql '{sentence}'"
    with selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            set_selectai_profile(cursor, llm_profile)
            set_vpd_appuser(cursor, user)
            cursor.execute(sql)
            cols = cursor.description
            _logger.debug(f"# cols: {cols}")
            if cols is None:
                return (["NO_DATA_FOUND"], [], [])
            else:
                header_data = [cols[c][0] for c in range(len(cols))]
                data = cursor.fetchall()
                raw_data = data
                for row in data:
                    _logger.debug(f"*** Row: {row} with cols {cols}")
                    if "could not be generated for you" in str(row[0]):
                        return (None, None, None)
                    if "No data found" in str(row[0]):
                        return (["NO_DATA_FOUND"], [], [])
                    row_json = dict()
                    result_array.append(row_json)
                    for c in range(len(row)):
                        row_json[cols[c][0]] = row[c]

    _logger.debug(f"### Result JSON(runsql): {result_array}")
    if not result_array:
        return (["NO_DATA_FOUND"], [], [])

    return (result_array, raw_data, header_data)


def runsql_custom(app_user: str, sentence: str, objects_profile: str) -> Optional[str]:
    _logger.debug(f"Running runsql_custom ...[{objects_profile}]")
    sql = f"""
        SELECT CUSTOM_SELECT_AI.RUNSQL(
            p_app_user      => '{app_user}',
            p_profile_name  => '{objects_profile}',
            p_text          => '{sentence}'
        ) FROM dual
    """

    rows = []
    with selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql):
                rows.append(result[0].read())

    return rows[0]


def query(
    user: Optional[str],
    sentence: str,
) -> tuple[Optional[List[any]], Optional[List[any]], Optional[List[str]]]:
    result_array = []
    raw_data = []
    header_data = []
    _logger.debug(f"Running SelectAI in pre-gen mode ...")
    _logger.debug(sentence)
    with selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            try:
                set_vpd_appuser(cursor, user)
                cursor.execute(sentence)
                cols = cursor.description
                _logger.debug(f"# cols: {cols}")
                if cols is None:
                    return (["NO_DATA_FOUND"], [], [])
                else:
                    header_data = [cols[c][0] for c in range(len(cols))]
                    _logger.debug(f"# header_data: {header_data}")
                    data = cursor.fetchall()
                    raw_data = data
                    for row in data:
                        _logger.debug(f"*** Row: {row} with cols {cols}")
                        row_json = dict()
                        result_array.append(row_json)
                        for c in range(len(row)):
                            row_json[cols[c][0]] = row[c]
            except DatabaseError as e:
                _logger.debug(str(e))
                return (None, None, None)

    _logger.debug(f"### Result JSON(query): {result_array}")
    if not result_array:
        return (["NO_DATA_FOUND"], [], [])

    return (result_array, raw_data, header_data)


def chat(
    user: Optional[str], sentence: str, llm_profile: str, debug: Optional[bool] = True
) -> str:
    sql = f"select ai chat '{sentence}'"
    with selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            set_selectai_profile(cursor, llm_profile)
            set_vpd_appuser(cursor, user)
            for result in cursor.execute(sql):
                if debug:
                    _logger.debug(f"*** Chat Output ***")
                    _logger.debug(result[0])
                    _logger.debug(f"*******************")
                return result[0]

    return "提示信息：系统根据您的问题，从数据库中没有找到相应的结果。"


def free_chat(
    sentence: str, llm_profile: str, debug: Optional[bool] = True
) -> Optional[str]:
    sql = (
        f"select ai chat 'system: 你的名字叫ChatBI，是一个专业的商业智能助手，能回答用户关于数据查询分析方面的相关问题。\n"
        f"user: {sentence} \n"
        f"assistant: \n'"
    )
    with selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            set_selectai_profile(cursor, llm_profile)
            for result in cursor.execute(sql):
                if debug:
                    _logger.debug(f"*** FreeChat Output ***")
                    _logger.debug(result[0])
                    _logger.debug(f"***********************")
                    return result[0]
    return None  # Expectation is that here is unreachable.


def set_selectai_profile(client: Cursor, llm_profile: str) -> None:
    client.callproc(
        "dbms_cloud_ai.set_profile",
        [llm_profile],
    )


def set_vpd_appuser(client: Cursor, user: str) -> None:
    if app_config.ENABLE_VPD:
        login = re.sub(r"_\d{14,}", "", user)
        client.callproc(
            "SET_APP_USER_CTX_PROC",
            [login],
        )
