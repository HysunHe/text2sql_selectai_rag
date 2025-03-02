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


def showsql(
    user: str, sentence: str, llm_profile: str, request_id: Optional[str] = None
) -> Optional[str]:
    _logger.debug(f"Running showsql ...[{llm_profile}]")
    sql = f"""
        SELECT CUSTOM_SELECT_AI.SHOWSQL(
            p_user      => '{user}',
            p_profile_name  => '{llm_profile}',
            p_text          => '{sentence}',
            p_request_id    => '{request_id}'
        ) FROM dual
    """

    rows = []
    with selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql):
                _logger.debug(result)
                rows.append(result[0])

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


def runsql2(
    user: Optional[str],
    sentence: str,
    llm_profile: str,
    request_id: Optional[str] = None,
) -> tuple[Optional[List[any]], Optional[List[any]], Optional[List[str]]]:
    sql = showsql(user, sentence, llm_profile, request_id)
    if sql is None:
        return (None, None, None)
    else:
        return query(user, sql)


def runsql(
    user: Optional[str],
    sentence: str,
    llm_profile: str,
    request_id: Optional[str] = None,
) -> tuple[Optional[List[any]], Optional[List[any]], Optional[List[str]]]:
    _logger.debug(f"Running runsql_direct ...[{llm_profile}]")
    sql = f"""
        SELECT CUSTOM_SELECT_AI.RUNSQL(
            p_user      => '{user}',
            p_profile_name  => '{llm_profile}',
            p_text          => '{sentence}',
            p_request_id    => '{request_id}'
        ) FROM dual
    """

    result_array = []
    with selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            try:
                set_vpd_appuser(cursor, user)
                cursor.execute(sql)
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
    user: Optional[str],
    sentence: str,
    llm_profile: str,
    system_prompt: Optional[str] = None,
    debug: Optional[bool] = True,
) -> str:
    _logger.debug(f"Running chat ...[{llm_profile}]")
    del user

    if system_prompt:
        sql = f"""
            SELECT CUSTOM_SELECT_AI.CHAT(
                p_profile_name  => '{llm_profile}',
                p_user_text     => '{sentence}',
                p_system_text   => '{system_prompt}'
            ) FROM dual
        """
    else:
        sql = f"""
            SELECT CUSTOM_SELECT_AI.CHAT(
                p_profile_name  => '{llm_profile}',
                p_user_text     => '{sentence}'
            ) FROM dual
        """

    rows = []
    with selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql):
                _logger.debug(result)
                rows.append(result[0])

    if debug:
        _logger.debug(f"*** Chat Output ***")
        _logger.debug(rows)
        _logger.debug(f"*******************")

    return rows[0]


def free_chat(
    user: Optional[str], sentence: str, llm_profile: str, debug: Optional[bool] = True
) -> Optional[str]:
    return chat(
        user=user,
        sentence=sentence,
        llm_profile=llm_profile,
        system_prompt="你的名字叫ChatBI，是一个专业的商业智能助手，能回答用户关于数据查询分析方面的相关问题。",
        debug=debug,
    )


def set_vpd_appuser(client: Cursor, user: str) -> None:
    if app_config.ENABLE_VPD:
        login = re.sub(r"_\d{14,}", "", user)
        client.callproc(
            "SET_APP_USER_CTX_PROC",
            [login],
        )
