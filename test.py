""" 
Description: 
 - AiReport project.

History:
 - 2025/02/11 by Hysun (hysun.he@oracle.com): Created
"""

import sys
import os
import json

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
print(f"Path: {path}")
if not path in sys.path:
    sys.path.insert(1, path)
del path

import logging
from service import selectai_biz_impl as svc
from dao import dao_sql
from conf import app_config

_logger = logging.getLogger(__name__)


if __name__ == "__main__":
    _logger.info("* Test Only *")
    _, params = dao_sql.get_selectai_prompt_by_intent("不良分布")
    param_array = None if not params else json.loads(params)
    params = svc.extract_params(
        user="Test",
        param_array=param_array,
        ask="公司为company2",
        profile=app_config.SELECTAI_PROFILE,
    )
    print(params)
    
    # kind = svc.determine_intent("Test", "只显示D1等级")
    # print(kind)
 