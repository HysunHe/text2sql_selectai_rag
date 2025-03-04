""" 
Description: 
 - AiReport project. This is a demo POC project, it is not intented
   for production. The quality of the code is not guaranteed. 
   
   If you refrence the code in this project, it means that you understand
   the risk and you are responsible for any issues caused by the code.

History:
 - 2025/01/20 by Hysun (hysun.he@oracle.com): Initial implementation.
"""

import logging
from dao import dao_sql
from appcache import result_cache, user_context

_logger = logging.getLogger(__name__)


def list_intents() -> list[any]:
    return dao_sql.list_completed_intents()


def list_utterances_by_intent(intent: str) -> list[any]:
    return dao_sql.list_utterances_by_intent(intent)


def add_utterances(intent: str, utternaces: str):
    sentences = utternaces.split("\n")
    for s in sentences:
        if not s.strip():
            sentences.remove(s)
    dao_sql.add_utterances(intent, sentences)


def delete_utterance(intent: str, key: str, utterance: str):
    dao_sql.delete_utterance(intent=intent, key=key, utterance=utterance)


def clear_cache(userId: str) -> list[any]:
    """Clear those cache entries belong to the specified user."""
    user_context.clear(user=userId)
    # result_cache.clear(prefix=userId)
    _logger.info(f"### Cache/Context cleared for user {userId}")


def clear_all() -> list[any]:
    user_context.clear_all()
    result_cache.clear_all()
    _logger.info(f"### All cache entries cleared.")
