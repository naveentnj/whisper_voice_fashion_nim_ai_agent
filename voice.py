import os
import sys
import pathlib
import requests
import torch
import soundfile as sf
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Local model paths (set by download_models.py)
_PROJECT_ROOT   = pathlib.Path(__file__).parent
LOCAL_MODELS    = _PROJECT_ROOT / "local_voice_models"
LOCAL_WHISPER   = LOCAL_MODELS / "whisper-large-v3"
LOCAL_OMNIVOICE = LOCAL_MODELS / "OmniVoice"

# Global singletons for local models
_omnivoice_model        = None
_local_whisper_pipeline = None

# -------------------------------------------------------------
# Lazy Loading Singletons for Local Models
# -------------------------------------------------------------

def get_omnivoice_model():
    """
    Lazy-loads OmniVoice.
    Priority: ./local_voice_models/OmniVoice  →  HF hub cache (k2-fsa/OmniVoice)
    """
    global _omnivoice_model
    if _omnivoice_model is None:
        print("Loading OmniVoice model onto local GPU (FP16)...")
        try:
            from omnivoice import OmniVoice
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
            dtype  = torch.float16 if torch.cuda.is_available() else torch.float32

            # Prefer local folder, fall back to HF hub id
            model_path = str(LOCAL_OMNIVOICE) if LOCAL_OMNIVOICE.exists() else "k2-fsa/OmniVoice"
            print(f"OmniVoice source: {model_path} | device={device} | dtype={dtype}")

            _omnivoice_model = OmniVoice.from_pretrained(
                model_path,
                device_map=device,
                dtype=dtype,
            )
            print("OmniVoice model loaded successfully.")
        except Exception as e:
            print(f"Error loading OmniVoice model: {e}")
            raise e
    return _omnivoice_model

def get_local_whisper_pipeline():
    """
    Lazy-loads Whisper-large-v3.
    Priority: ./local_voice_models/whisper-large-v3  →  HF hub (openai/whisper-large-v3)
    """
    global _local_whisper_pipeline
    if _local_whisper_pipeline is None:
        print("Loading local Whisper model...")
        try:
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

            device      = "cuda:0" if torch.cuda.is_available() else "cpu"
            torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

            # Prefer local folder, fall back to HF hub id
            model_id = str(LOCAL_WHISPER) if LOCAL_WHISPER.exists() else "openai/whisper-large-v3"
            print(f"Whisper source: {model_id} | device={device} | dtype={torch_dtype}")

            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True,
            )
            model.to(device)
            processor = AutoProcessor.from_pretrained(model_id)

            _local_whisper_pipeline = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
                max_new_tokens=128,
                chunk_length_s=30,
                batch_size=16,
                return_timestamps=True,
                torch_dtype=torch_dtype,
                device=device,
            )
            print("Local Whisper model loaded successfully.")
        except Exception as e:
            print(f"Error loading local Whisper model: {e}")
            raise e
    return _local_whisper_pipeline

# -------------------------------------------------------------
# Core Voice API Interface
# -------------------------------------------------------------

def transcribe_audio(audio_path: str, mode: str = "online") -> str:
    """
    Transcribes a local audio file.
    Modes:
    - 'online': Call Hugging Face serverless Whisper API (0MB local VRAM).
    - 'offline': Run Whisper-large-v3 locally on your GPU (requires loading weights).
    """
    if mode == "offline":
        return _transcribe_offline(audio_path)
    else:
        return _transcribe_online(audio_path)

def _transcribe_online(audio_path: str) -> str:
    if not HF_API_KEY:
        raise ValueError("HUGGINGFACE_API_KEY is not set in the environment.")
    
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    print(f"Transcribing audio file {audio_path} via HF Whisper-large-v3 Cloud API...")
    url = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    with open(audio_path, "rb") as f:
        data = f.read()
        
    try:
        response = requests.post(url, headers=headers, data=data, timeout=30)
        
        # Handle Hugging Face model loading delay (503 status)
        if response.status_code == 503:
            print("HF Cloud Model is loading, waiting and retrying...")
            import time
            time.sleep(5)
            response = requests.post(url, headers=headers, data=data, timeout=30)
            
        if response.status_code != 200:
            raise RuntimeError(f"HF Whisper API error (HTTP {response.status_code}): {response.text}")
            
        result = response.json()
        transcription = result.get("text", "").strip()
        print(f"Cloud transcription result: '{transcription}'")
        return transcription
    except Exception as e:
        print(f"Cloud transcription failed, attempting local fallback... Error: {e}")
        # Graceful fallback to local if cloud fails
        return _transcribe_offline(audio_path)

def _transcribe_offline(audio_path: str) -> str:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
    pipe = get_local_whisper_pipeline()
    print(f"Transcribing audio file {audio_path} locally on GPU...")
    try:
        # Load audio using soundfile
        data, samplerate = sf.read(audio_path)
        
        # Convert stereo to mono if necessary
        if len(data.shape) > 1:
            data = data.mean(axis=1)
            
        # Format for Hugging Face pipeline (handles resampling to 16kHz automatically)
        audio_input = {
            "raw": data,
            "sampling_rate": samplerate
        }
        
        result = pipe(audio_input)
        text = result.get("text", "").strip()
        print(f"Local transcription result: '{text}'")
        return text
    except Exception as e:
        print(f"Local transcription failed: {e}")
        raise e

def synthesize_speech(text: str, output_path: str, mode: str = "online", reference_audio: str = None, reference_text: str = None) -> str:
    """
    Synthesizes speech.
    Modes:
    - 'online': Generate lightweight cloud speech via gTTS (0MB local VRAM).
    - 'offline': Generate luxury voice locally via OmniVoice (GPU accelerated).
    """
    if mode == "offline":
        return _synthesize_offline(text, output_path, reference_audio, reference_text)
    else:
        return _synthesize_online(text, output_path)

def _synthesize_online(text: str, output_path: str) -> str:
    print(f"Generating online speech using gTTS for text: '{text}'...")
    try:
        from gtts import gTTS
        # High quality British female accent ('co.uk')
        tts = gTTS(text=text, lang='en', tld='co.uk')
        
        # Note: gtts outputs mp3 format, which html5 decodes perfectly under any path
        tts.save(output_path)
        print(f"Online speech saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Online gTTS synthesis failed: {e}")
        raise e

def _synthesize_offline(text: str, output_path: str, reference_audio: str = None, reference_text: str = None) -> str:
    model = get_omnivoice_model()
    
    print(f"Generating offline speech using OmniVoice for text: '{text}'...")
    try:
        if reference_audio and os.path.exists(reference_audio):
            print(f"Using Voice Cloning with reference: {reference_audio}")
            audio = model.generate(
                text=text,
                ref_audio=reference_audio,
                ref_text=reference_text
            )
        else:
            # Voice Design mode - warm, friendly female assistant
            print("Using designed voice: 'female, low pitch, warm tone, clear speech'")
            audio = model.generate(
                text=text,
                instruct="female, low pitch, warm tone, clear speech"
            )
            
        # Write output wav file (OmniVoice outputs 24kHz audio)
        sf.write(output_path, audio[0], 24000)
        print(f"Offline voice saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Offline OmniVoice synthesis failed: {e}")
        raise e

# -------------------------------------------------------------
# CLI Utility - Model Downloader
# -------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--download-all":
        print("=========================================================")
        print("VALENTI AI - Local Model Downloader & Cache Initializer")
        print("=========================================================")
        
        # 1. Download OmniVoice
        print("\n[1/2] Fetching OmniVoice weights...")
        try:
            get_omnivoice_model()
            print(">> OmniVoice weights are cached successfully.")
        except Exception as e:
            print(">> Failed to cache OmniVoice:", e)
            
        # 2. Download Whisper
        print("\n[2/2] Fetching Whisper-large-v3 weights...")
        try:
            get_local_whisper_pipeline()
            print(">> Whisper-large-v3 weights are cached successfully.")
        except Exception as e:
            print(">> Failed to cache Whisper-large-v3:", e)
            
        print("\nModel caching process completed!")
        
    elif len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running standalone speech module diagnostics...")
        test_out = "test_online.wav"
        try:
            synthesize_speech("Testing cloud speech synthesis", test_out, mode="online")
            print("Test 1 (Online gTTS Synthesis) SUCCESS.")
        except Exception as e:
            print("Test 1 (Online gTTS Synthesis) FAILED:", e)
            
        if os.path.exists(test_out):
            try: os.remove(test_out)
            except: pass
    else:
        print("Voice module imported successfully.")
        print("Use '--download-all' flag to cache both Whisper and OmniVoice models locally.")
