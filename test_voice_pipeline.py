"""
Direct Voice Pipeline Test — bypasses browser entirely.
Generates a known audio clip, then tests Whisper transcription.
Run with: uv run python test_voice_pipeline.py
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "static", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

print("=" * 60)
print("  VOICE PIPELINE DIRECT TEST")
print("=" * 60)

# ── Step 1: Generate a test audio file using gTTS ──
print("\n[Step 1] Generating test audio via gTTS...")
test_text = "Hello, this is a test of the whisper speech recognition system."
test_mp3 = os.path.join(AUDIO_DIR, "pipeline_test.mp3")
test_wav = os.path.join(AUDIO_DIR, "pipeline_test.wav")

try:
    from gtts import gTTS
    tts = gTTS(text=test_text, lang='en', tld='co.uk')
    tts.save(test_mp3)
    print(f"  Generated MP3: {os.path.getsize(test_mp3)} bytes")
except Exception as e:
    print(f"  FAILED to generate audio: {e}")
    sys.exit(1)

# Convert MP3 to WAV (Whisper works best with WAV)
try:
    import subprocess
    # Try ffmpeg first
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", test_mp3, "-ar", "16000", "-ac", "1", test_wav],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0:
        print(f"  Converted to WAV: {os.path.getsize(test_wav)} bytes")
    else:
        print(f"  ffmpeg failed: {result.stderr[:200]}")
        print("  Will test with MP3 directly.")
        test_wav = test_mp3
except FileNotFoundError:
    print("  ffmpeg not found. Will test with MP3 directly.")
    test_wav = test_mp3

# ── Step 2: Test ONLINE Whisper (HuggingFace API) ──
print("\n[Step 2] Testing ONLINE Whisper (HuggingFace Cloud API)...")
import voice

try:
    result_online = voice.transcribe_audio(test_wav, mode="online")
    if result_online:
        print(f"  ONLINE SUCCESS: '{result_online}'")
    else:
        print(f"  ONLINE returned EMPTY string (silence)")
except Exception as e:
    print(f"  ONLINE FAILED: {e}")

# ── Step 3: Test OFFLINE Whisper (Local GPU) ──
print("\n[Step 3] Testing OFFLINE Whisper (Local GPU)...")
try:
    result_offline = voice.transcribe_audio(test_wav, mode="offline")
    if result_offline:
        print(f"  OFFLINE SUCCESS: '{result_offline}'")
    else:
        print(f"  OFFLINE returned EMPTY string (silence)")
except Exception as e:
    print(f"  OFFLINE FAILED: {e}")

# ── Step 4: Test with WebM format (what the browser sends) ──
print("\n[Step 4] Testing if soundfile can read WebM format...")
try:
    import soundfile as sf
    data, sr = sf.read(test_wav)
    print(f"  soundfile can read WAV: {len(data)} samples, {sr}Hz")
except Exception as e:
    print(f"  soundfile FAILED on WAV: {e}")

print("\n" + "=" * 60)
print("  Expected transcription: '" + test_text + "'")
print("=" * 60)

# Cleanup
for f in [test_mp3, test_wav]:
    if os.path.exists(f) and f != test_wav:
        os.remove(f)
