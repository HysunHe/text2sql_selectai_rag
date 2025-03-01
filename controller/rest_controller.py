""" 
Description: 
 - AiReport project.

History:
 - 2025/01/20 by Hysun (hysun.he@oracle.com): Created
"""

import os
import logging
import markdown
import time
from fastapi import FastAPI, Body, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from dto.JsonResponse import ChatMessage
from conf import app_config
from applog import my_logger as log_utils
from service import selectai_biz_impl as svc
from service import admin_service as admin

_logger = logging.getLogger(__name__)
_app = FastAPI(
    openapi_url=f"{app_config.CONTEXT_ROOT}/openapi.json",
    docs_url=f"{app_config.CONTEXT_ROOT}/docs",
)
_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def app() -> FastAPI:
    return _app


@_app.get(f"{app_config.CONTEXT_ROOT}/hello")
def hello(user: str = Query(default="Username", examples=["Hysun"])):
    _logger.info(f"# Hello {user}")
    time.sleep(3)
    _logger.info("# Done")
    return {"status": "Success"}


@_app.get(f"{app_config.CONTEXT_ROOT}/readme")
def readme():
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    with open(f"{path}/README.md", "r") as file:
        md_str = file.read()
    html_str = markdown.markdown(md_str).replace("\\", "<br>")
    return HTMLResponse(content=html_str, status_code=200)


@_app.get(f"{app_config.CONTEXT_ROOT}/chat/list_intents")
@log_utils.debug_enabled(_logger)
def list_intents():
    return admin.list_intents()


@_app.get(f"{app_config.CONTEXT_ROOT}/chat/list_utterances")
@log_utils.debug_enabled(_logger)
def list_utterances(intent: str = Query(..., description="intent")):
    return admin.list_utterances_by_intent(intent)


@_app.post(f"{app_config.CONTEXT_ROOT}/chat/add_utterances")
@log_utils.debug_enabled(_logger)
def add_utterances(
    intent: str = Body(..., description="intent"),
    utterances: str = Body(..., description="example questions"),
):
    admin.add_utterances(intent, utterances)
    return "OK"


@_app.post(f"{app_config.CONTEXT_ROOT}/chat/delete_utterance")
@log_utils.debug_enabled(_logger)
def delete_utterance(
    intent: str = Body(..., description="intent"),
    key: str = Body(..., description="primary key or rowid"),
    utterance: str = Body(..., description="utterance"),
):
    admin.delete_utterance(intent=intent, key=key, utterance=utterance)
    return "OK"


@_app.post(f"{app_config.CONTEXT_ROOT}/chat/with_selectai")
@log_utils.debug_enabled(_logger)
def with_selectai(
    user: str = Body(..., description="current user"),
    ask: str = Body(..., description="query"),
):
    try:
        data = svc.execute_query(user, ask)
        return ChatMessage(data=data, status="OK", err_msg="")
    except Exception as e:
        _logger.error(f"Error >>> {str(e)} ")
        if "Request Timeout" in str(e):
            msg = "大语言模型服务调用超时，请稍候重试！"
        elif "ORA-20429" in str(e):
            msg = (
                "大语言模型服务调用次数超限，您可能需要更换API Key，或者等待额度刷新！"
            )
        else:
            _logger.error(msg=e, stack_info=True)
            msg = f"错误: {str(e)}"

        data = [{"content": msg, "source": "system", "score": 1}]
        return ChatMessage(data=data, status="ERROR", err_msg=str(e))


@_app.post(f"{app_config.CONTEXT_ROOT}/chat/clear_history")
@log_utils.debug_enabled(_logger)
def clear_history(
    userId: str = Body(description="userId"),
):
    admin.clear_cache(userId)
    return ChatMessage(data=[], status="OK", err_msg="")


@_app.post(f"{app_config.CONTEXT_ROOT}/chat/clear_cache_all")
@log_utils.debug_enabled(_logger)
def clear_cache_all():
    admin.clear_cache
    return ChatMessage(data=[], status="OK", err_msg="")
