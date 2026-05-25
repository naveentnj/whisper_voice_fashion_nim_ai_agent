"""
download_models.py
==================
Downloads Whisper-large-v3 and OmniVoice into the local folder:

    ./local_voice_models/whisper-large-v3/    (~3 GB)
    ./local_voice_models/OmniVoice/           (~2 GB)

Usage:
    python download_models.py               # Download BOTH models
    python download_models.py --whisper     # Download Whisper only
    python download_models.py --omnivoice   # Download OmniVoice only
    python download_models.py --status      # Check what's downloaded

Voice pipeline priority:
    Offline mode -> local_voice_models/ folder first
    Fallback      -> HuggingFace cache (~/.cache/huggingface/hub/)
    Cloud mode    -> HuggingFace Inference API (no local storage)
"""
import io, sys
# Force UTF-8 output on Windows so progress symbols render correctly
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import os
import sys
import time
import pathlib
import shutil
from datetime import datetime
from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────
PROJECT_ROOT  = pathlib.Path(__file__).parent.resolve()
LOCAL_MODELS  = PROJECT_ROOT / "local_voice_models"
WHISPER_DIR   = LOCAL_MODELS / "whisper-large-v3"
OMNIVOICE_DIR = LOCAL_MODELS / "OmniVoice"

# Load HF token from .env (optional but increases rate limits)
load_dotenv(PROJECT_ROOT / ".env")
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY", None)

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def hr(char="─", n=55):
    print(char * n)

def folder_size_mb(path: pathlib.Path) -> float:
    """Return total size of a folder in MB."""
    total = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return total / (1024 ** 2)

def is_complete(path: pathlib.Path, min_files: int = 3) -> bool:
    """A download is considered complete if the folder has ≥ min_files files."""
    if not path.exists():
        return False
    files = [f for f in path.rglob("*") if f.is_file()]
    return len(files) >= min_files

# ─────────────────────────────────────────────────────────────
# Download: Whisper large-v3  (~3 GB)
# ─────────────────────────────────────────────────────────────

def download_whisper():
    hr("═")
    print("  [1/2]  openai/whisper-large-v3")
    hr("═")
    print(f"  Target folder : {WHISPER_DIR}")
    print(f"  Approx. size  : ~3 GB (PyTorch weights only)")
    print(f"  HF Token      : {'present ✓' if HF_TOKEN else 'not set (public download)'}")

    if is_complete(WHISPER_DIR):
        sz = folder_size_mb(WHISPER_DIR)
        print(f"\n  ✅  Already downloaded  ({sz:.0f} MB on disk)")
        print(f"      Path: {WHISPER_DIR}\n")
        return True

    print("\n  Starting download …  (this may take 5-15 min on a typical connection)")
    LOCAL_MODELS.mkdir(parents=True, exist_ok=True)

    try:
        from huggingface_hub import snapshot_download
        t0 = time.time()

        snapshot_download(
            repo_id              = "openai/whisper-large-v3",
            local_dir            = str(WHISPER_DIR),
            local_dir_use_symlinks = False,        # Windows-safe: copies files, no symlinks
            token                = HF_TOKEN,
            ignore_patterns      = [               # Skip non-PyTorch weights to save space
                "*.msgpack",
                "flax_model*",
                "tf_model*",
                "rust_model*",
                "onnx/*",
            ],
        )

        elapsed = time.time() - t0
        sz = folder_size_mb(WHISPER_DIR)
        print(f"\n  ✅  Whisper-large-v3 downloaded!")
        print(f"      Size    : {sz:.0f} MB")
        print(f"      Time    : {elapsed/60:.1f} min")
        print(f"      Path    : {WHISPER_DIR}\n")
        return True

    except Exception as e:
        print(f"\n  ❌  Download failed: {e}")
        print("      Tip: Ensure you have a stable internet connection.")
        print("           Add HUGGINGFACE_API_KEY to .env for authenticated access.\n")
        return False


# ─────────────────────────────────────────────────────────────
# Download: OmniVoice  (~2 GB)
# ─────────────────────────────────────────────────────────────

def download_omnivoice():
    hr("═")
    print("  [2/2]  k2-fsa/OmniVoice  (Massively Multilingual Zero-Shot TTS)")
    hr("═")
    print(f"  Target folder : {OMNIVOICE_DIR}")
    print(f"  Approx. size  : ~2 GB")
    print(f"  HF Token      : {'present ✓' if HF_TOKEN else 'not set (public download)'}")

    if is_complete(OMNIVOICE_DIR):
        sz = folder_size_mb(OMNIVOICE_DIR)
        print(f"\n  ✅  Already downloaded  ({sz:.0f} MB on disk)")
        print(f"      Path: {OMNIVOICE_DIR}\n")
        return True

    print("\n  Starting download …  (this may take 5-10 min on a typical connection)")
    LOCAL_MODELS.mkdir(parents=True, exist_ok=True)

    try:
        from huggingface_hub import snapshot_download
        t0 = time.time()

        snapshot_download(
            repo_id              = "k2-fsa/OmniVoice",
            local_dir            = str(OMNIVOICE_DIR),
            local_dir_use_symlinks = False,        # Windows-safe
            token                = HF_TOKEN,
        )

        elapsed = time.time() - t0
        sz = folder_size_mb(OMNIVOICE_DIR)
        print(f"\n  ✅  OmniVoice downloaded!")
        print(f"      Size    : {sz:.0f} MB")
        print(f"      Time    : {elapsed/60:.1f} min")
        print(f"      Path    : {OMNIVOICE_DIR}\n")
        return True

    except Exception as e:
        print(f"\n  ❌  Download failed: {e}")
        print("      Tip: Check internet connection and HF token permissions.\n")
        return False


# ─────────────────────────────────────────────────────────────
# Status Reporter
# ─────────────────────────────────────────────────────────────

def check_status():
    hr()
    print("  VALENTI AI – Voice Model Status")
    hr()

    hf_cache = pathlib.Path.home() / ".cache" / "huggingface" / "hub"

    # ── Whisper ──
    local_w  = is_complete(WHISPER_DIR)
    hf_w     = any(hf_cache.glob("models--openai--whisper-large-v3*"))

    if local_w:
        sz = folder_size_mb(WHISPER_DIR)
        status_w = f"✅  local_voice_models/whisper-large-v3/  ({sz:.0f} MB)"
    elif hf_w:
        status_w = "✅  HF cache  (~/.cache/huggingface/hub/)"
    else:
        status_w = "❌  NOT DOWNLOADED"

    print(f"  Whisper-large-v3  : {status_w}")

    # ── OmniVoice ──
    local_o  = is_complete(OMNIVOICE_DIR)
    hf_o     = any(hf_cache.glob("models--k2-fsa--OmniVoice*"))

    if local_o:
        sz = folder_size_mb(OMNIVOICE_DIR)
        status_o = f"✅  local_voice_models/OmniVoice/  ({sz:.0f} MB)"
    elif hf_o:
        status_o = "✅  HF cache  (~/.cache/huggingface/hub/)"
    else:
        status_o = "❌  NOT DOWNLOADED"

    print(f"  OmniVoice         : {status_o}")

    # ── Offline readiness ──
    offline_ok = (local_w or hf_w) and (local_o or hf_o)
    hr()
    if offline_ok:
        print("  Offline mode  : ✅  READY")
        print("  Cloud mode    : ✅  READY  (uses HuggingFace API + gTTS)")
    else:
        missing = []
        if not (local_w or hf_w):
            missing.append("Whisper")
        if not (local_o or hf_o):
            missing.append("OmniVoice")
        print(f"  Offline mode  : ❌  NOT READY  (missing: {', '.join(missing)})")
        print(f"  Fix           :  python download_models.py")
    hr()
    print()
    return offline_ok


# ─────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "--all"

    print()
    hr("═")
    print("  VALENTI AI – Local Voice Model Downloader")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    hr("═")
    print(f"  Download folder  : {LOCAL_MODELS}")
    print(f"  Total disk space : ~5 GB required")
    print()

    # ── Status only ──
    if arg == "--status":
        check_status()
        sys.exit(0)

    # ── Download Whisper ──
    whisper_ok = True
    if arg in ("--all", "--whisper"):
        whisper_ok = download_whisper()

    # ── Download OmniVoice ──
    omnivoice_ok = True
    if arg in ("--all", "--omnivoice"):
        omnivoice_ok = download_omnivoice()

    # ── Final summary ──
    print()
    hr("═")
    print("  DOWNLOAD SUMMARY")
    hr("═")
    if arg in ("--all", "--whisper"):
        print(f"  Whisper-large-v3  : {'✅ OK' if whisper_ok else '❌ FAILED'}")
    if arg in ("--all", "--omnivoice"):
        print(f"  OmniVoice         : {'✅ OK' if omnivoice_ok else '❌ FAILED'}")
    print()

    check_status()

    if whisper_ok and omnivoice_ok:
        print("  🎉  Both models ready! Start the server with:")
        print("       uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        print()
    else:
        print("  ⚠️   Some downloads failed. Retry with:  python download_models.py")
        print()
        sys.exit(1)
