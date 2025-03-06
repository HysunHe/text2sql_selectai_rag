""" 
Description: 
 - AiReport project.

History:
 - 2024/07/11 by Hysun (hysun.he@oracle.com): Created
"""

import os
from dotenv import load_dotenv

load_dotenv("../app.env")

# Database connection information
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = int(os.environ.get("DB_PORT", 1521))
DB_SERVICE = os.environ.get("DB_SERVICE")
DB_USER = os.environ.get("DB_USER")
DB_PWD = os.environ.get("DB_PWD")
DB_POOL_MIN = int(os.environ.get("DB_POOL_MIN", 1))
DB_POOL_MAX = int(os.environ.get("DB_POOL_MAX", 2))

# Vector search parameters
# Distance matrics list: COSINE, EUCLIDEAN, DOT, MANHATTAN, HAMMING
DISTANCE_THRESHOLD = float(os.environ.get("DISTANCE_THRESHOLD", 0.25))
DISTANCE_THRESHOLD_ACCURATE = float(os.environ.get("DISTANCE_THRESHOLD_ACCURATE", 0.05))

# SelectAI parameters
SELECTAI_PROFILE = os.environ.get("SELECTAI_PROFILE")

# Data security
ENABLE_VPD = bool(os.environ.get("ENABLE_VPD", "FALSE").upper() == "TRUE")

# Application server
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_LISTEN_PORT = int(os.environ.get("SERVER_LISTEN_PORT", 5000))
CONTEXT_ROOT = os.environ.get("CONTEXT_ROOT", "")

# Embedding model
EMBEDDING_CONFIG = os.environ.get("EMBEDDING_CONFIG", "DEFAULT")

# Application debug level
DEBUG_LEVEL = int(os.environ.get("DEBUG_LEVEL", 10))
LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH")
