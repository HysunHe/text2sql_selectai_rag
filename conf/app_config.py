""" 
Description: 
 - AiReport project.

History:
 - 2024/07/11 by Hysun (hysun.he@oracle.com): Created
"""

import os
from dotenv import load_dotenv

load_dotenv("app.env")

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
DISTANCE_MATRIC = os.environ.get("DISTANCE_MATRIC", "COSINE")
NEAREST_TOPN = int(os.environ.get("NEAREST_TOPN", 10))
DISTANCE_THRESHOLD = float(os.environ.get("DISTANCE_THRESHOLD", 0.25))
DISTANCE_THRESHOLD_ACCURATE = float(os.environ.get("DISTANCE_THRESHOLD_ACCURATE", 0.05))

# SelectAI database connections.
SELECTAI_DB_USER = os.environ.get("SELECTAI_DB_USER")
SELECTAI_DB_PWD = os.environ.get("SELECTAI_DB_PWD")
SELECTAI_DSN = os.environ.get("SELECTAI_DSN")
SELECTAI_WALLET = os.environ.get("SELECTAI_WALLET")
SELECTAI_WALLET_PASSWORD = os.environ.get("SELECTAI_WALLET_PASSWORD")
SELECTAI_DB_POOL_MIN = int(os.environ.get("SELECTAI_DB_POOL_MIN", 1))
SELECTAI_DB_POOL_MAX = int(os.environ.get("SELECTAI_DB_POOL_MAX", 2))

# SelectAI parameters
SELECTAI_PROFILE = os.environ.get("SELECTAI_PROFILE")

# Data security
ENABLE_VPD = bool(os.environ.get("ENABLE_VPD", "FALSE").upper() == "TRUE")

# Application server
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_LISTEN_PORT = int(os.environ.get("SERVER_LISTEN_PORT", 5000))
CONTEXT_ROOT = os.environ.get("CONTEXT_ROOT", "")

# OCI Generative AI Service
OCI_GENAI_COMPARTMENT = os.environ.get("OCI_GENAI_COMPARTMENT")
OCI_CONFIG_FILE = os.environ.get("OCI_CONFIG_FILE", "~/.oci/config")
OCI_CONFIG_PROFILE = os.environ.get("OCI_CONFIG_PROFILE", "DEFAULT")
OCI_SERVICE_ENDPOINT = os.environ.get("OCI_SERVICE_ENDPOINT")
OCI_GENAI_MODEL = os.environ.get("OCI_GENAI_MODEL")

# Application debug level
DEBUG_LEVEL = int(os.environ.get("DEBUG_LEVEL", 10))
LOG_FILE_PATH = os.environ.get("LOG_FILE_PATH")

# Embedding model
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL")

# RAG settings
RAG_DOC_PATH = os.environ.get("RAG_DOC_PATH")
RAG_DOC_VIEWER = os.environ.get("RAG_DOC_VIEWER")
