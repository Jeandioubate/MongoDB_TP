"""
db.py — Singleton de connexion à MongoDB
"""

from pymongo import MongoClient
from MongoTp.config import MONGO_URI, DB_NAME

_client = None
_db     = None


def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URI)
        _db     = _client[DB_NAME]
    return _db


def close_db():
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db     = None
