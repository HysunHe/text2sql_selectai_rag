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
import oracledb
import logging
from aimodels import app_embedding
from dao import db_pool
from conf import app_config
from typing import Optional

_logger = logging.getLogger(__name__)


def list_similar_intents(ask: str) -> str:
    intents = []
    sql = """
        SELECT 
            INTENT,
            ABS(VECTOR_DISTANCE(INTENT_EMBEDDING, vector(:1), COSINE)) as distance
        FROM HKE_SUPERVISED_QUESTIONS
        ORDER BY distance
        FETCH FIRST 10 ROWS ONLY
    """
    query_vector = app_embedding.embedding_model.embed_documents([ask])[0]
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql, [str(query_vector)]):
                _logger.debug(f"{result[0]} | {round(result[1], 6)}")
                intents.append(result[0])
    return "\n".join(intents)


def list_all_intents() -> str:
    intents = []
    sql = "SELECT INTENT FROM HKE_SUPERVISED_QUESTIONS"
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql):
                intents.append(result[0])
    return "\n".join(intents)


def list_chat_intents() -> str:
    intents = []
    sql = "SELECT INTENT FROM HKE_SUPERVISED_QUESTIONS WHERE SELECTAI_PROMPT IS NULL and SQL_TEXT IS NULL"
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql):
                intents.append(result[0])
    return "\n".join(intents)


def list_selectai_intents() -> str:
    intents = []
    sql = (
        "SELECT INTENT FROM HKE_SUPERVISED_QUESTIONS WHERE SELECTAI_PROMPT IS NOT NULL"
    )
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql):
                intents.append(result[0])
    return "\n".join(intents)


def list_companies() -> str:
    services = []
    sql = "SELECT DISTINCT COMPANY FROM HKE_PROD_OUT_YIELD_QTY"
    with db_pool.selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.callproc(
                "SET_APP_USER_CTX_PROC",
                [""],
            )
            for result in cursor.execute(sql):
                services.append(result[0])
    return "\n".join(services)


def list_factories() -> str:
    intents = []
    sql = "SELECT DISTINCT FACTORYNAME FROM HKE_PROD_OUT_YIELD_QTY"
    with db_pool.selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.callproc(
                "SET_APP_USER_CTX_PROC",
                [""],
            )
            for result in cursor.execute(sql):
                intents.append(result[0])
    return "\n".join(intents)


def list_products() -> str:
    intents = []
    sql = "SELECT DISTINCT PRODUCT FROM HKE_PROD_OUT_YIELD_QTY"
    with db_pool.selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.callproc(
                "SET_APP_USER_CTX_PROC",
                [""],
            )
            for result in cursor.execute(sql):
                intents.append(result[0])
    return "\n".join(intents)


def list_grades() -> str:
    intents = []
    sql = "SELECT DISTINCT GRADE FROM HKE_PROD_OUT_YIELD_QTY"
    with db_pool.selectai_pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.callproc(
                "SET_APP_USER_CTX_PROC",
                [""],
            )
            for result in cursor.execute(sql):
                intents.append(result[0])
    return "\n".join(intents)


def populate_chat_history() -> str:
    sql = "SELECT INTENT, EXAMPLE_QUESTION FROM HKE_QUESTION_EXAMPLES"
    results = []
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql):
                result_tuple = (result[1], result[0])
                results.append(result_tuple)
    chat_history = []
    for pair in results:
        utterance, intent = pair
        chat_history.append(f"Human: {utterance}\nAI: {intent}\n")
    return "\n".join(chat_history)


def get_intent_from_intent_embedding(
    ask: str, accuracy_distance: Optional[float] = app_config.DISTANCE_THRESHOLD
) -> Optional[str]:
    sql = """
        SELECT 
            INTENT,
            ABS(VECTOR_DISTANCE(INTENT_EMBEDDING, vector(:1), COSINE)) as distance
        FROM HKE_SUPERVISED_QUESTIONS
        ORDER BY distance
        FETCH FIRST 3 ROWS ONLY
    """
    query_vector = app_embedding.embedding_model.embed_documents([ask])[0]

    result_tuple = None
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql, [str(query_vector)]):
                _logger.debug(f"{result[0]} | {round(result[1], 6)}")
                if result_tuple is None:
                    result_tuple = (result[0], round(result[1], 6))

    if result_tuple is None:
        return None

    intent, distance = result_tuple
    if distance > accuracy_distance:
        return None

    return intent


def check_intent_distance(
    ask: str,
    intent: str,
    accuracy_distance: Optional[float] = app_config.DISTANCE_THRESHOLD,
) -> bool:
    sql = """
        SELECT 
            ABS(VECTOR_DISTANCE(vector(:1), vector(:2), COSINE)) as distance
        FROM DUAL
    """
    ask_vector = app_embedding.embedding_model.embed_query(ask)
    intent_vector = app_embedding.embedding_model.embed_query(intent)

    distance = None
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql, [str(ask_vector), str(intent_vector)]):
                distance = round(result[0], 6)
                _logger.debug(f"Intent distance: {round(result[0], 6)}")

    return distance <= accuracy_distance


def get_accurate_intent_by_intent_embedding(ask: str) -> Optional[str]:
    return get_intent_from_intent_embedding(
        ask=ask, accuracy_distance=app_config.DISTANCE_THRESHOLD_ACCURATE
    )


def get_intent_by_utterance(
    ask: str, accuracy_distance: Optional[float] = app_config.DISTANCE_THRESHOLD
) -> Optional[str]:
    sql = """
        SELECT 
            INTENT,
            EXAMPLE_QUESTION,
            ABS(VECTOR_DISTANCE(QUESTION_EMBEDDING, vector(:1), COSINE)) as distance
        FROM HKE_QUESTION_EXAMPLES
        ORDER BY distance
        FETCH FIRST 3 ROWS ONLY
    """
    query_vector = app_embedding.embedding_model.embed_documents([ask])[0]

    result_tuple = None
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql, [str(query_vector)]):
                _logger.debug(f"{result[0]} | {result[1]} | {round(result[2], 6)}")
                if result_tuple is None:
                    result_tuple = (result[0], result[1], round(result[2], 6))

    if result_tuple is None:
        return None

    intent, _, distance = result_tuple
    if distance > accuracy_distance:
        return None

    return intent


def get_accurate_intent_by_utterance(ask: str) -> Optional[str]:
    return get_intent_by_utterance(
        ask=ask, accuracy_distance=app_config.DISTANCE_THRESHOLD_ACCURATE
    )


def get_selectai_prompt_by_intent(intent: str) -> tuple[Optional[str], Optional[str]]:
    result_tuple: tuple[Optional[str], Optional[str]] = None
    sql = (
        "SELECT SELECTAI_PROMPT, PARAMS FROM HKE_SUPERVISED_QUESTIONS WHERE INTENT = :1"
    )
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql, [intent]):
                result_tuple = (result[0], result[1])
                break
    if not result_tuple:
        return None
    selectai_prompt, _ = result_tuple
    _logger.debug(f"selectai prompt: {selectai_prompt}")
    return result_tuple


def get_chart_by_intent(
    intent: str,
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    sql = "SELECT CHART_TYPE, CHART_DATA_COLS, CHART_NAME_COLS, EXT_REPORT_URL FROM HKE_SUPERVISED_QUESTIONS WHERE INTENT = :1"
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql, [intent]):
                return (result[0], result[1], result[2], result[3])
    return None


def get_selectai_profile_by_intent(intent: str = None) -> Optional[str]:
    if not intent:
        return app_config.SELECTAI_PROFILE

    selectai_profile = app_config.SELECTAI_PROFILE
    sql = "SELECT SELECTAI_PROFILE FROM HKE_SUPERVISED_QUESTIONS WHERE INTENT = :1"
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            for result in cursor.execute(sql, [intent]):
                selectai_profile = result[0]
                break

    selectai_profile = (
        app_config.SELECTAI_PROFILE if not selectai_profile else selectai_profile
    )
    _logger.debug(f"selectai profile for {intent}: {selectai_profile}")
    return selectai_profile


def get_selectai_prompt(ask: str) -> Optional[str]:
    intent = get_intent_by_utterance(ask)
    if not intent:
        return None
    return get_selectai_prompt_by_intent(intent)


def list_completed_intents() -> list[any]:
    _logger.debug("### list_completed_intents ...")
    result_array = []
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT INTENT, SELECTAI_PROMPT, PARAMS FROM HKE_SUPERVISED_QUESTIONS"
            )
            cols = cursor.description
            data = cursor.fetchall()
            for row in data:
                row_json = dict()
                result_array.append(row_json)
                for c in range(len(row)):
                    row_json[cols[c][0]] = row[c]
    _logger.debug(f"### got intents: {len(result_array)}")
    return result_array


def list_utterances_by_intent(intent: str) -> list[any]:
    _logger.debug("### list_utterances_by_intent ...")
    result_array = []
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT ROWID, INTENT, EXAMPLE_QUESTION FROM HKE_QUESTION_EXAMPLES WHERE INTENT = :1",
                [intent],
            )
            cols = cursor.description
            data = cursor.fetchall()
            for row in data:
                row_json = dict()
                result_array.append(row_json)
                for c in range(len(row)):
                    row_json[cols[c][0]] = row[c]
    _logger.debug(f"### got utterances: {len(result_array)}")
    return result_array


def delete_utterance(intent: str, key: str, utterance: str):
    _logger.debug(f"### delete_utterance for {intent}: {utterance}")
    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM HKE_QUESTION_EXAMPLES WHERE ROWID = :1", [key])
            _logger.debug(
                f"### delete_utterance for {intent}: {utterance}: {cursor.rowcount}"
            )
            connection.commit()


def add_utterances(intent: str, examples: list[str]):
    _logger.debug(f"### add_utterances for {intent}:\n{examples}")
    start = time.perf_counter()
    embeddings = app_embedding.embedding_model.embed_documents(list(examples))
    end = time.perf_counter()
    _logger.debug(f"### Embedding done. Cost seconds: {round(end - start, 3)}")

    with db_pool.vectordb_pool.acquire() as connection:
        with connection.cursor() as cursor:
            cursor.setinputsizes(
                oracledb.DB_TYPE_VARCHAR,
                oracledb.DB_TYPE_VARCHAR,
                oracledb.DB_TYPE_VECTOR,
            )
            cursor.executemany(
                "INSERT INTO HKE_QUESTION_EXAMPLES (INTENT, EXAMPLE_QUESTION, QUESTION_EMBEDDING) VALUES (:1, :2, vector(:3))",
                list(
                    zip(
                        [intent for _ in examples],
                        examples,
                        [str(e) for e in embeddings],
                    )
                ),
            )
            _logger.debug(f"### add_utterances for {intent}: {cursor.rowcount}")
            connection.commit()

    end = time.perf_counter()
    _logger.debug(f"### Done. Total elapsed seconds: {round(end - start, 3)}")
