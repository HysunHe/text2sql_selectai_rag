""" 
Description: 
 - AiReport project. This is a demo POC project, it is not intented
   for production. The quality of the code is not guaranteed. 
   
   If you refrence the code in this project, it means that you understand
   the risk and you are responsible for any issues caused by the code.

History:
 - 2025/01/20 by Hysun (hysun.he@oracle.com): Initial implementation.
"""

import pydantic
from pydantic import BaseModel


class Response:
    """DTO class"""

    def __init__(self) -> None:
        self._success = None
        self._code = None
        self._message = None
        self._data = None

    @property
    def success(self):
        return self._success

    @success.setter
    def success(self, val: bool):
        self._success = val

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, val: int):
        self._code = val

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, val: str):
        self._message = val

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, val: any):
        self._data = val


class ChatMessage(BaseModel):
    data: list = pydantic.Field(..., description="Response text")
    status: str = pydantic.Field(..., description="Response text")
    err_msg: str = pydantic.Field(..., description="Response text")

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {"content": "xxx", "score": 1, "source": "llm"},
                    {"content": "yyy", "score": 0.7, "source": "source file url"},
                ],
                "status": "success",
                "err_msg": "",
            }
        }


class AskResponseData:
    content: str = ""
    source: str = ""
    score: float = 0.0

    def __init__(self, content, source, score):
        self.content = content
        self.source = source
        self.score = score
