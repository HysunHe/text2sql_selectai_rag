""" 
Description: 
 - AiReport project.

History:
 - 2024/07/11 by Hysun (hysun.he@oracle.com): Created
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
