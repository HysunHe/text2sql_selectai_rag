""" 
Description: 
 - AiReport project. This is a demo POC project, it is not intented
   for production. The quality of the code is not guaranteed. 
   
   If you refrence the code in this project, it means that you understand
   the risk and you are responsible for any issues caused by the code.

History:
 - 2025/01/20 by Hysun (hysun.he@oracle.com): Initial implementation.
"""

import re
import logging
from dao.db_pool import selectai_pool
from conf import app_config
from myutils import util_funcs
from oracledb import Cursor
from oracledb import DatabaseError
from ast import literal_eval
from typing import List, Optional

_logger = logging.getLogger(__name__)


def embedding_invoke(
    docs: List[str], config_name: Optional[str] = app_config.EMBEDDING_CONFIG
) -> List[List[float]]:
    _logger.debug(f"Running embedding.")
    rows = []
    with selectai_pool.acquire() as connection:
        for text in docs:
            with connection.cursor() as cursor:
                sql = f"""
                    SELECT CUSTOM_SELECT_AI.EMBEDDING(
                        p_text              => '{text}',
                        p_embedding_conf    => '{config_name}'
                    ) FROM dual
                """
                for result in cursor.execute(sql):
                    rows.append(literal_eval(result[0]))
    return rows


def showsql(
    user: str,
    sentence: str,
    llm_profile: str,
    request_id: Optional[str] = None,
    config_name: Optional[str] = app_config.EMBEDDING_CONFIG,
) -> Optional[str]:
    _logger.debug(f"Running showsql ...[{llm_profile}]")
    sql = f"""
        SELECT CUSTOM_SELECT_AI.SHOWSQL(
            p_user              => '{user}',
            p_profile_name      => '{llm_profile}',
            p_user_text         => '{util_funcs.escape(sentence)}',
            p_embedding_conf    => '{config_name}',
            p_request_id        => '{request_id}'
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


def runsql(
    user: Optional[str],
    sentence: str,
    llm_profile: str,
    request_id: Optional[str] = None,
    config_name: Optional[str] = app_config.EMBEDDING_CONFIG,
) -> tuple[Optional[List[any]], Optional[List[any]], Optional[List[str]]]:
    sql = showsql(
        user=user,
        sentence=sentence,
        llm_profile=llm_profile,
        request_id=request_id,
        config_name=config_name,
    )
    _logger.debug(sql)
    if sql is None:
        return (None, None, None)
    else:
        return query(user, sql)


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
                p_user_text     => '{util_funcs.escape(sentence)}',
                p_system_text   => '{util_funcs.escape(system_prompt)}'
            ) FROM dual
        """
    else:
        sql = f"""
            SELECT CUSTOM_SELECT_AI.CHAT(
                p_profile_name  => '{llm_profile}',
                p_user_text     => '{util_funcs.escape(sentence)}'
            ) FROM dual
        """

    rows = []
    with selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql):
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
        try:
            client.callproc(
                "SET_APP_USER_CTX_PROC",
                [login],
            )
        except Exception as e:
            _logger.error(str(e))
            _logger.error(
                "VPD is enabled, but failed to set the user info to the database session context. Check if you defined the procedure SET_APP_USER_CTX_PROC."
            )
