"""
VALENTI AI – FastAPI Backend  v2.0
Managed by Uvicorn | MongoDB via pymongo | NIM via langchain-nvidia-ai-endpoints
"""
import os
import json
import uuid
from typing import Dict, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import voice
import agents

# ─────────────────────────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="VALENTI AI Couture Storefront",
    version="2.0.0",
    description="Voice-driven luxury fashion store powered by NVIDIA NIM, CrewAI, Whisper & OmniVoice",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR   = os.path.join(os.path.dirname(__file__), "static")
AUDIO_DIR    = os.path.join(STATIC_DIR, "audio")
PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), "products.json")
os.makedirs(AUDIO_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────
# Startup: Sync products JSON → MongoDB
# ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    try:
        from database import sync_products_to_mongo, ping_db, track_event, seed_default_users
        status = ping_db()
        print(f"[DB] MongoDB status: {status['status']}")
        if status["status"] == "connected":
            with open(PRODUCTS_FILE) as f:
                prods = json.load(f)
            n = sync_products_to_mongo(prods)
            print(f"[DB] Synced {n} products to MongoDB")
            seed_default_users()
            track_event("server_start", {"products_synced": n})
    except Exception as e:
        print(f"[DB] Startup sync skipped (MongoDB may not be running): {e}")


# ─────────────────────────────────────────────────────────────────
# Static & Index
# ─────────────────────────────────────────────────────────────────
@app.get("/")
def get_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Frontend index.html not found.")
    return FileResponse(index_path)


# ─────────────────────────────────────────────────────────────────
# Products API
# ─────────────────────────────────────────────────────────────────
@app.get("/api/products")
def get_products(category: str = "", query: str = "", max_price: float = 999999):
    """Serve products – tries MongoDB first, falls back to JSON file."""
    try:
        from database import get_products_from_mongo, ping_db
        if ping_db()["status"] == "connected":
            products = get_products_from_mongo(category=category, query=query, max_price=max_price)
            if products:
                return products
    except Exception:
        pass

    # Fallback: JSON file
    if not os.path.exists(PRODUCTS_FILE):
        raise HTTPException(status_code=500, detail="Products catalog not found.")
    with open(PRODUCTS_FILE) as f:
        products = json.load(f)

    # Apply filters if given
    if category:
        products = [p for p in products if p.get("category") == category]
    if query:
        q = query.lower()
        products = [p for p in products if q in p.get("name", "").lower()
                    or q in p.get("description", "").lower()]
    if max_price < 999999:
        products = [p for p in products if p.get("price", 0) <= max_price]

    return products


# ─────────────────────────────────────────────────────────────────
# Voice Chat API
# ─────────────────────────────────────────────────────────────────
@app.post("/api/voice-chat")
async def post_voice_chat(
    file:       UploadFile = File(...),
    cart:       str  = Form(...),
    asr_mode:   str  = Form("online"),
    tts_mode:   str  = Form("online"),
    session_id: str  = Form(""),
):
    """
    Full voice pipeline:
    1. Transcribe audio (Whisper cloud or local GPU)
    2. Run CrewAI agents with NVIDIA NIM LLM + tool calling
    3. Save session to MongoDB
    4. Synthesize spoken reply (gTTS cloud or OmniVoice GPU)
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    # Parse cart
    try:
        current_cart = json.loads(cart)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid cart JSON: {e}")

    # Save audio
    temp_voice_path = os.path.join(AUDIO_DIR, f"input_{session_id}.wav")
    try:
        content = await file.read()
        with open(temp_voice_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save audio: {e}")

    # Transcribe
    try:
        transcription = voice.transcribe_audio(temp_voice_path, mode=asr_mode)
    except Exception as e:
        if os.path.exists(temp_voice_path):
            os.remove(temp_voice_path)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")
    finally:
        if os.path.exists(temp_voice_path):
            os.remove(temp_voice_path)

    # Handle silence
    if not transcription:
        silent_msg = "I didn't quite catch that — please tap the microphone and speak clearly."
        audio_filename = f"reply_{session_id}.{'wav' if tts_mode=='offline' else 'mp3'}"
        out_path = os.path.join(AUDIO_DIR, audio_filename)
        voice.synthesize_speech(silent_msg, out_path, mode=tts_mode)
        return {
            "session_id":    session_id,
            "transcription": "[Silence]",
            "response":      silent_msg,
            "cart":          current_cart,
            "audio_url":     f"/static/audio/{audio_filename}",
        }

    # Agent flow (NIM LLM + tool calling + MongoDB logging)
    print(f"[Voice] '{transcription}' | asr={asr_mode} tts={tts_mode}")
    agent_result = await agents.run_agent_flow_async(
        user_input=transcription,
        current_cart=current_cart,
        session_id=session_id,
        asr_mode=asr_mode,
        tts_mode=tts_mode,
    )
    response_text = agent_result["response"]
    updated_cart  = agent_result["cart"]

    # Synthesize reply
    audio_filename = f"reply_{session_id}.{'wav' if tts_mode=='offline' else 'mp3'}"
    response_audio_path = os.path.join(AUDIO_DIR, audio_filename)
    audio_url = None
    try:
        voice.synthesize_speech(response_text, response_audio_path, mode=tts_mode)
        audio_url = f"/static/audio/{audio_filename}"
    except Exception as e:
        print(f"[Voice] TTS failed (text-only fallback): {e}")

    # Track analytics (best-effort)
    try:
        from database import track_event
        track_event("voice_chat", {
            "asr_mode": asr_mode,
            "tts_mode": tts_mode,
            "words": len(transcription.split()),
        }, session_id=session_id)
    except Exception:
        pass

    return {
        "session_id":    session_id,
        "transcription": transcription,
        "response":      response_text,
        "cart":          updated_cart,
        "audio_url":     audio_url,
        "actions":       agent_result.get("actions", []),
    }


# ─────────────────────────────────────────────────────────────────
# Raw Test Bench APIs
# ─────────────────────────────────────────────────────────────────

@app.post("/api/test-asr")
async def test_asr(
    file: UploadFile = File(...),
    asr_mode: str = Form("offline")
):
    """Test ASR strictly (Audio -> Text)"""
    session_id = str(uuid.uuid4())
    temp_voice_path = os.path.join(AUDIO_DIR, f"test_asr_{session_id}.wav")
    try:
        content = await file.read()
        print(f"[TestASR] Received audio: {len(content)} bytes | filename={file.filename} | content_type={file.content_type} | mode={asr_mode}")
        if len(content) < 100:
            print(f"[TestASR] WARNING: Audio file is very small ({len(content)} bytes), likely empty recording")
        with open(temp_voice_path, "wb") as f:
            f.write(content)
        transcription = voice.transcribe_audio(temp_voice_path, mode=asr_mode)
        print(f"[TestASR] Transcription result: '{transcription}'")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"ASR failed: {e}")
    finally:
        if os.path.exists(temp_voice_path):
            os.remove(temp_voice_path)

    return {"transcription": transcription}


@app.post("/api/test-llm")
async def test_llm(
    text: str = Form(...)
):
    """Test LLM strictly (Text -> Text)"""
    agent_result = await agents.run_agent_flow_async(
        user_input=text,
        current_cart={},
    )
    return {"response": agent_result["response"]}


@app.post("/api/test-tts")
def test_tts(
    text: str = Form(...),
    tts_mode: str = Form("offline")
):
    """Test TTS strictly (Text -> Audio)"""
    session_id = str(uuid.uuid4())
    audio_filename = f"test_tts_{session_id}.{'wav' if tts_mode=='offline' else 'mp3'}"
    out_path = os.path.join(AUDIO_DIR, audio_filename)
    try:
        voice.synthesize_speech(text, out_path, mode=tts_mode)
        audio_url = f"/static/audio/{audio_filename}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")

    return {"audio_url": audio_url}


# ─────────────────────────────────────────────────────────────────
# Checkout API
# ─────────────────────────────────────────────────────────────────
class CheckoutRequest(BaseModel):
    cart:       Dict[str, int]
    tts_mode:   Optional[str] = "online"
    session_id: Optional[str] = ""

@app.post("/api/checkout")
def post_checkout(request: CheckoutRequest):
    cart       = request.cart
    tts_mode   = request.tts_mode or "online"
    session_id = request.session_id or str(uuid.uuid4())

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty.")

    with open(PRODUCTS_FILE) as f:
        catalog = json.load(f)

    items, total = [], 0.0
    for pid, qty in cart.items():
        p = next((prod for prod in catalog if prod["id"] == pid), None)
        if p:
            total += p["price"] * qty
            items.append(f"{qty}x {p['name']}")

    message = (
        f"Thank you for your order! Your purchase of {', '.join(items)} "
        f"for a total of ${total:.2f} has been processed. We hope to see you again!"
    )

    # Persist order to MongoDB
    order_id = ""
    try:
        from database import save_order, track_event
        order_id = save_order(cart=cart, total=total, items=items, session_id=session_id)
        track_event("checkout", {"total": total, "item_count": len(items)}, session_id=session_id)
        print(f"[DB] Order saved: {order_id}")
    except Exception as e:
        print(f"[DB] Order save skipped: {e}")

    # Synthesize thank-you audio
    audio_filename = f"checkout_{session_id}.{'wav' if tts_mode=='offline' else 'mp3'}"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)
    try:
        voice.synthesize_speech(message, audio_path, mode=tts_mode)
        audio_url = f"/static/audio/{audio_filename}"
    except Exception as e:
        print(f"[Voice] Checkout TTS error: {e}")
        audio_url = None

    return {
        "success":  True,
        "order_id": order_id,
        "message":  message,
        "items":    items,
        "total":    round(total, 2),
        "audio_url": audio_url,
    }


# ─────────────────────────────────────────────────────────────────
# Admin / Status Endpoints
# ─────────────────────────────────────────────────────────────────
@app.get("/api/db-status")
def db_status():
    """MongoDB connection health check."""
    try:
        from database import ping_db
        return ping_db()
    except ImportError:
        return {"status": "module_missing", "error": "database.py not found"}

@app.get("/api/orders")
def get_orders(limit: int = 20):
    """Return most recent orders from MongoDB."""
    try:
        from database import get_orders
        return get_orders(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
def get_sessions(limit: int = 50):
    """Return recent voice session logs from MongoDB."""
    try:
        from database import get_sessions
        return get_sessions(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health():
    """Full system health check."""
    import torch
    db_ok = False
    try:
        from database import ping_db
        db_ok = ping_db()["status"] == "connected"
    except Exception:
        pass

    return {
        "server":       "VALENTI AI v2.0",
        "status":       "running",
        "gpu_available": torch.cuda.is_available(),
        "gpu_name":     torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU",
        "mongodb":      "connected" if db_ok else "disconnected (orders saved in-memory)",
        "nim_model":    "moonshotai/kimi-k2.6",
        "whisper":      "openai/whisper-large-v3 (cloud + local GPU)",
        "tts":          "gTTS (cloud) | OmniVoice (local GPU)",
    }

@app.get("/api/model-status")
def model_status():
    """Check which local models are cached on disk."""
    import pathlib
    hf_cache = pathlib.Path.home() / ".cache" / "huggingface" / "hub"

    whisper_cached  = any(hf_cache.glob("models--openai--whisper-large-v3*"))
    omnivoice_cached = any(hf_cache.glob("models--k2-fsa--OmniVoice*"))

    # Check for local_voice_models folder
    local_dir = pathlib.Path(__file__).parent / "local_voice_models"
    local_whisper   = (local_dir / "whisper-large-v3").exists()
    local_omnivoice = (local_dir / "OmniVoice").exists()

    return {
        "hf_cache": {
            "whisper_large_v3": whisper_cached,
            "omnivoice":        omnivoice_cached,
            "cache_path":       str(hf_cache),
        },
        "local_voice_models": {
            "whisper_large_v3": local_whisper,
            "omnivoice":        local_omnivoice,
            "folder":           str(local_dir),
        },
        "offline_ready": (whisper_cached or local_whisper) and (omnivoice_cached or local_omnivoice),
    }


# ─────────────────────────────────────────────────────────────────
# Auth & Cart APIs
# ─────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    username: str
    password: str

class CartUpdateRequest(BaseModel):
    username: str
    product_id: str
    quantity: int = 1

class CartSaveRequest(BaseModel):
    username: str
    items: Dict[str, int]

@app.post("/api/login")
def api_login(req: LoginRequest):
    """Authenticate a user against MongoDB."""
    try:
        from database import login_user
        result = login_user(req.username, req.password)
        if result.get("error"):
            raise HTTPException(status_code=401, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cart/{username}")
def api_get_cart(username: str):
    """Load user's cart from MongoDB."""
    try:
        from database import get_user_cart
        items = get_user_cart(username)
        return {"username": username, "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cart")
def api_save_cart(req: CartSaveRequest):
    """Save full cart state to MongoDB."""
    try:
        from database import save_user_cart
        save_user_cart(req.username, req.items)
        return {"status": "saved", "username": req.username, "items": req.items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/cart/{username}")
def api_clear_cart(username: str):
    """Clear a user's cart."""
    try:
        from database import clear_user_cart
        clear_user_cart(username)
        return {"status": "cleared", "username": username}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────
# Mount Static Files  (MUST be last)
# ─────────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=["static/audio/*", "*.log"],
        log_level="info",
    )
