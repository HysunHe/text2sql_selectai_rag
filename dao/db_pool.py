""" 
Description: 
 - AiReport project.

History:
 - 2024/07/11 by Hysun (hysun.he@oracle.com): Created
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