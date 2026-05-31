"""
database.py - MongoDB / Motor async database layer for VALENTI AI
Uses pymongo for sync operations and motor for async FastAPI routes.
"""
import os
from datetime import datetime, timezone

UTC = timezone.utc
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import numpy as np

# Lazy loaded vector index
_vector_index = None
_embedding_model = None
_int_to_str_id = {}
_str_to_int_id = {}

# ─────────────────────────────────────────────
# Connection Configuration
# ─────────────────────────────────────────────
# Primary: MongoDB Atlas (cloud)   MONGODB_URI
# Fallback: localhost              MONGODB_URI_LOCAL
MONGO_URI_PRIMARY = os.getenv("MONGODB_URI", "")
MONGO_URI_LOCAL   = os.getenv("MONGODB_URI_LOCAL", "mongodb://localhost:27017")
DB_NAME           = os.getenv("MONGODB_DB", "valenti_ai")

_sync_client: Optional[MongoClient] = None
_active_uri: str = ""

def get_db():
    """
    Return the synchronous MongoDB database handle (lazy singleton).
    Tries Atlas URI first; falls back to localhost automatically.
    """
    global _sync_client, _active_uri
    if _sync_client is None:
        uris = [u for u in [MONGO_URI_PRIMARY, MONGO_URI_LOCAL] if u]
        for uri in uris:
            try:
                client = MongoClient(uri, serverSelectionTimeoutMS=3000,
                                     connectTimeoutMS=3000, tls=True if "mongodb+srv" in uri else False)
                client[DB_NAME].command("ping")   # fast connectivity check
                _sync_client = client
                _active_uri  = uri
                label = "Atlas" if "mongodb+srv" in uri else "localhost"
                print(f"[DB] Connected to MongoDB {label}: {DB_NAME}")
                break
            except Exception as e:
                print(f"[DB] Could not connect to {uri[:40]}... : {e}")
        if _sync_client is None:
            raise ConnectionFailure("Could not connect to any MongoDB URI.")
    return _sync_client[DB_NAME]


def ping_db() -> Dict[str, Any]:
    """Test connection; return status dict."""
    try:
        db = get_db()
        db.command("ping")
        label = "Atlas (cloud)" if "mongodb+srv" in _active_uri else "localhost"
        return {"status": "connected", "backend": label, "db": DB_NAME}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}


# ─────────────────────────────────────────────
# Collections helpers
# ─────────────────────────────────────────────

def orders_col():
    return get_db()["orders"]

def sessions_col():
    return get_db()["sessions"]

def analytics_col():
    return get_db()["analytics"]

def products_col():
    return get_db()["products"]


def users_col():
    return get_db()["users"]

def carts_col():
    return get_db()["carts"]


# ─────────────────────────────────────────────
# Orders
# ─────────────────────────────────────────────

def save_order(cart: Dict[str, int], total: float, items: List[str],
               session_id: str = "", user_agent: str = "") -> str:
    """
    Persist a completed order to MongoDB.
    Returns the inserted document _id as string.
    """
    doc = {
        "session_id": session_id,
        "cart":       cart,
        "items":      items,
        "total":      round(total, 2),
        "status":     "placed",
        "user_agent": user_agent,
        "created_at": datetime.now(UTC),
    }
    result = orders_col().insert_one(doc)
    return str(result.inserted_id)


def get_orders(limit: int = 20) -> List[Dict]:
    """Return the most recent orders (for admin / analytics)."""
    docs = orders_col().find({}, {"_id": 0}).sort("created_at", DESCENDING).limit(limit)
    return list(docs)


# ─────────────────────────────────────────────
# Voice Session Logging
# ─────────────────────────────────────────────

def log_voice_session(session_id: str, transcription: str, response: str,
                      asr_mode: str, tts_mode: str, cart_snapshot: Dict) -> str:
    """Store each voice interaction for audit / training / analytics."""
    doc = {
        "session_id":    session_id,
        "transcription": transcription,
        "response":      response,
        "asr_mode":      asr_mode,
        "tts_mode":      tts_mode,
        "cart_snapshot": cart_snapshot,
        "created_at":    datetime.now(UTC),
    }
    result = sessions_col().insert_one(doc)
    return str(result.inserted_id)


def get_sessions(limit: int = 50) -> List[Dict]:
    """Return recent voice session logs."""
    docs = sessions_col().find({}, {"_id": 0}).sort("created_at", DESCENDING).limit(limit)
    return list(docs)


# ─────────────────────────────────────────────
# User Authentication (simple hash-based)
# ─────────────────────────────────────────────
import hashlib

def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username: str, password: str) -> Dict[str, Any]:
    """Register a new user. Returns user doc or error."""
    col = users_col()
    if col.find_one({"username": username}):
        return {"error": "User already exists"}
    doc = {
        "username": username,
        "password_hash": _hash_password(password),
        "created_at": datetime.now(UTC),
    }
    col.insert_one(doc)
    return {"username": username, "status": "created"}

def login_user(username: str, password: str) -> Dict[str, Any]:
    """Validate credentials. Returns user info or error."""
    col = users_col()
    user = col.find_one({"username": username})
    if not user:
        return {"error": "User not found"}
    if user["password_hash"] != _hash_password(password):
        return {"error": "Invalid password"}
    return {"username": username, "status": "ok"}

def seed_default_users():
    """Create default users if they don't exist."""
    defaults = [
        {"username": "kevin1",   "password": "4r3rbio"},
        {"username": "eleven2",  "password": "9y7gf487"},
    ]
    for u in defaults:
        result = register_user(u["username"], u["password"])
        if result.get("status") == "created":
            print(f"[DB] Seeded user: {u['username']}")
        else:
            print(f"[DB] User already exists: {u['username']}")


# ─────────────────────────────────────────────
# Cart Persistence (per-user, stored in MongoDB)
# ─────────────────────────────────────────────

def get_user_cart(username: str) -> Dict[str, int]:
    """Load the user's persisted cart from MongoDB."""
    doc = carts_col().find_one({"username": username})
    if doc:
        return doc.get("items", {})
    return {}

def save_user_cart(username: str, cart_items: Dict[str, int]) -> None:
    """Upsert the user's cart to MongoDB."""
    carts_col().update_one(
        {"username": username},
        {"$set": {"items": cart_items, "updated_at": datetime.now(UTC)}},
        upsert=True,
    )

def clear_user_cart(username: str) -> None:
    """Clear a user's cart."""
    carts_col().delete_one({"username": username})


# ─────────────────────────────────────────────
# Product Catalog Sync (JSON → MongoDB)
# ─────────────────────────────────────────────

def sync_products_to_mongo(products: List[Dict]) -> int:
    """
    Upsert all products from products.json into MongoDB.
    Idempotent – safe to call on every server start.
    Returns count of upserted documents.
    """
    col = products_col()
    upserted = 0
    for p in products:
        result = col.update_one(
            {"id": p["id"]},
            {"$set": {**p, "updated_at": datetime.now(UTC)}},
            upsert=True,
        )
        if result.upserted_id or result.modified_count:
            upserted += 1
    return upserted


def get_products_from_mongo(category: str = "", query: str = "",
                             max_price: float = 999999) -> List[Dict]:
    """Query products from MongoDB with optional filters."""
    col = products_col()
    filt: Dict[str, Any] = {"price": {"$lte": max_price}}
    if category:
        filt["category"] = category
    if query:
        filt["$or"] = [
            {"name":        {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
        ]
    docs = col.find(filt, {"_id": 0, "embedding": 0})
    return list(docs)

def init_vector_index():
    """Fetch embeddings from MongoDB and build turbovec index."""
    global _vector_index, _embedding_model, _int_to_str_id, _str_to_int_id
    from turbovec import IdMapIndex
    from sentence_transformers import SentenceTransformer
    
    print("[DB] Initializing vector index...")
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
    docs = list(products_col().find({"embedding": {"$exists": True}}))
    if not docs:
        print("[DB] No embeddings found. Vector index is empty.")
        return

    dim = len(docs[0]["embedding"])
    _vector_index = IdMapIndex(dim=dim, bit_width=4)
    
    vectors = []
    ids = []
    for i, doc in enumerate(docs):
        int_id = np.uint64(i + 1)
        str_id = doc["id"]
        _int_to_str_id[int_id] = str_id
        _str_to_int_id[str_id] = int_id
        
        vectors.append(doc["embedding"])
        ids.append(int_id)
        
    _vector_index.add_with_ids(np.array(vectors, dtype=np.float32), np.array(ids, dtype=np.uint64))
    print(f"[DB] Vector index initialized with {len(docs)} products.")

def vector_search_products(query: str, top_k: int = 5, category: str = "", max_price: float = 999999) -> List[Dict]:
    """Search products using semantic vector search and pre-filtering."""
    global _vector_index, _embedding_model, _int_to_str_id
    
    if _vector_index is None:
        init_vector_index()
        
    if _vector_index is None:
        # Fallback to text search if initialization failed
        return get_products_from_mongo(category, query, max_price)
        
    query_vector = _embedding_model.encode(query)
    
    # Pre-filtering: get allowed int ids based on category and price
    filt = {"price": {"$lte": max_price}, "embedding": {"$exists": True}}
    if category:
        filt["category"] = category
        
    allowed_docs = list(products_col().find(filt, {"id": 1}))
    allowed_str_ids = {doc["id"] for doc in allowed_docs}
    allowed_int_ids = np.array([_str_to_int_id[sid] for sid in allowed_str_ids if sid in _str_to_int_id], dtype=np.uint64)
    
    if len(allowed_int_ids) == 0:
        return []

    # Search the vector index
    scores, int_ids = _vector_index.search(np.array([query_vector], dtype=np.float32), k=top_k, allowlist=allowed_int_ids)
    
    # Retrieve full documents from MongoDB
    matched_str_ids = [_int_to_str_id[iid] for iid in int_ids[0]]
    
    # Fetch in order of relevance
    pipeline = [
        {"$match": {"id": {"$in": matched_str_ids}}},
        {"$addFields": {"__order": {"$indexOfArray": [matched_str_ids, "$id"]}}},
        {"$sort": {"__order": 1}},
        {"$project": {"_id": 0, "embedding": 0, "__order": 0}}
    ]
    
    return list(products_col().aggregate(pipeline))


# ─────────────────────────────────────────────
# Analytics Events
# ─────────────────────────────────────────────

def track_event(event: str, data: Dict = None, session_id: str = "") -> None:
    """Fire-and-forget analytics event logger."""
    try:
        analytics_col().insert_one({
            "event":      event,
            "data":       data or {},
            "session_id": session_id,
            "ts":         datetime.now(UTC),
        })
    except Exception:
        pass  # Never crash the app over analytics


# ─────────────────────────────────────────────
# CLI: test connection
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import json
    result = ping_db()
    print(json.dumps(result, indent=2))
    if result["status"] == "connected":
        # seed test
        import sys, pathlib
        products_file = pathlib.Path(__file__).parent / "products.json"
        if products_file.exists():
            with open(products_file) as f:
                prods = json.load(f)
            n = sync_products_to_mongo(prods)
            print(f"Synced {n} products to MongoDB collection '{DB_NAME}.products'")
