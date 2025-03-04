""" 
Description: 
 - AiReport project. This is a demo POC project, it is not intented
   for production. The quality of the code is not guaranteed. 
   
   If you refrence the code in this project, it means that you understand
   the risk and you are responsible for any issues caused by the code.

History:
 - 2025/01/20 by Hysun (hysun.he@oracle.com): Initial implementation.
"""

import sys
import os
import uvicorn

path = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
print(f"Path: {path}")
if not path in sys.path:
    sys.path.insert(1, path)
del path

import logging
from conf import app_config
from controller import rest_controller
from applog import my_logger as log_utils

_logger = logging.getLogger(__name__)


@log_utils.debug_enabled(_logger)
def run():
    """Run the WSGI server"""
    host = app_config.SERVER_HOST
    port = app_config.SERVER_LISTEN_PORT
    _logger.info(f"# WSGI server listening at {host}:{port}")
    uvicorn.run(rest_controller.app(), host=host, port=port)


if __name__ == "__main__":
    run()
