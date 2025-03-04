""" 
Description: 
 - AiReport project. This is a demo POC project, it is not intented
   for production. The quality of the code is not guaranteed. 
   
   If you refrence the code in this project, it means that you understand
   the risk and you are responsible for any issues caused by the code.

History:
 - 2025/01/20 by Hysun (hysun.he@oracle.com): Initial implementation.
"""

import oracledb
from conf import app_config

vectordb_pool = oracledb.create_pool(
    user=app_config.DB_USER,
    password=app_config.DB_PWD,
    dsn=f"{app_config.DB_HOST}:{app_config.DB_PORT}/{app_config.DB_SERVICE}",
    min=app_config.DB_POOL_MIN,
    max=app_config.DB_POOL_MAX,
)

selectai_pool = vectordb_pool