# modules/db.py
from pymongo import MongoClient
from datetime import datetime
from typing import Optional, Dict, Any, List
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

class Database:
    def __init__(self, uri: str = MONGO_URI, db_name: str = "facial_analysis"):
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[db_name]
        self.users = self.db["users"]
        self.records = self.db["analysis_records"]
        # Indexes
        self.users.create_index("email", unique=True)
        self.records.create_index([("user_id", 1), ("timestamp", -1)])

    # ---------- AUTH ----------
    def create_user(self, name: str, email: str, password_hash: str) -> bool:
        try:
            self.users.insert_one({
                "name": name,
                "email": email,
                "password_hash": password_hash,
                "created_at": datetime.utcnow()
            })
            return True
        except Exception:
            return False

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.users.find_one({"email": email})

    # ---------- ANALYSIS ----------
    def save_analysis(self, user_id: str, module: str, payload: Dict[str, Any]) -> str:
        doc = {
            "user_id": user_id,
            "module": module,
            "timestamp": datetime.utcnow(),
            "data": payload,
        }
        result = self.records.insert_one(doc)
        return str(result.inserted_id)

    def get_user_records(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        docs = list(
            self.records.find({"user_id": user_id})
            .sort("timestamp", -1)
            .limit(limit)
        )
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs
