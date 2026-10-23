"""
Voiceover Agent Core Synthesizer (Dual Engine: Kokoro-82M & Edge Neural)
With Dramatic Word-Stretching & Terminal Phrase Lengthening
"""

import os
import asyncio
from datetime import datetime
import soundfile as sf
import edge_tts
from humanizer import humanize_cadence

# Check if Kokoro ONNX is available
KOKORO_AVAILABLE = False
_kokoro_instance = None

try:
    from kokoro_onnx import Kokoro
    _model_path = os.path.join(os.path.dirname(__file__), "models", "kokoro-v1.0.onnx")
    _voices_path = os.path.join(os.path.dirname(__file__), "models", "voices-v1.0.bin")
    if os.path.exists(_model_path) and os.path.exists(_voices_path):
        _kokoro_instance = Kokoro(_model_path, _voices_path)
        KOKORO_AVAILABLE = True
except Exception as e:
    print(f"[Kokoro Initialization Notice]: {e}")

# Unified Voice Profiles
VOICE_PROFILES = {
    # Kokoro-82M Next-Gen SOTA Voices
    "kokoro_adam": {
        "name": "Adam (Kokoro SOTA Deep Voice)",
        "engine": "kokoro",
        "voice_id": "am_adam",
        "gender": "Male",
        "badge": "Kokoro 82M",
        "description": "Ultra-realistic American male. Incredible vowel elongation and emotional gravity."
    },
    "kokoro_michael": {
        "name": "Michael (Kokoro Dramatic Storyteller)",
        "engine": "kokoro",
        "voice_id": "am_michael",
        "gender": "Male",
        "badge": "Kokoro 82M",
        "description": "Dynamic cadence with breath pauses. Ideal for high-retention video hooks."
    },
    "kokoro_sarah": {
        "name": "Sarah (Kokoro Expressive Female)",
        "engine": "kokoro",
        "voice_id": "af_sarah",
        "gender": "Female",
        "badge": "Kokoro 82M",
        "description": "Natural human inflections without robotic clipped endings."
    },
    "kokoro_george": {
        "name": "George (Kokoro British Narrator)",
        "engine": "kokoro",
        "voice_id": "bm_george",
        "gender": "Male",
        "badge": "Kokoro 82M",
        "description": "Sophisticated British storytelling with natural terminal slowdown."
    },
    # Azure Edge Neural Voices
    "marcus": {
        "name": "Marcus (Deep Documentary Baritone)",
        "engine": "edge",
        "voice_id": "en-US-ChristopherNeural",
        "gender": "Male",
        "badge": "Azure Neural",
        "description": "Deep, authoritative, and cinematic. Great for trailers and crime mysteries."
    },
    "sarah_edge": {
        "name": "Sarah (Empathetic Storyteller)",
        "engine": "edge",
        "voice_id": "en-US-AvaMultilingualNeural",
        "gender": "Female",
        "badge": "Azure Neural",
        "description": "Warm, caring, and natural. Excellent for emotional advice and podcasts."
    },
    "james": {
        "name": "James (Viral Podcast Host)",
        "engine": "edge",
        "voice_id": "en-US-AndrewMultilingualNeural",
        "gender": "Male",
        "badge": "Azure Neural",
        "description": "Authentic and energetic. Perfect for YouTube intros and TikTok/Reels."
    }
}

async def generate_voiceover(
    text: str,
    voice_key: str = "kokoro_adam",
    rate_adj: str = "+0%",
    pitch_adj: str = "+0Hz",
    output_path: str = None,
    stretch_words: bool = True,
    preprocess: bool = True
) -> str:
    """
    Synthesizes speech with word stretching and terminal lengthening.
    """
    profile = VOICE_PROFILES.get(voice_key.lower(), VOICE_PROFILES["kokoro_adam"])
    engine = profile.get("engine", "kokoro")

    # 1. Humanize & Apply Terminal Lengthening (Prevents clipped robotic endings)
    should_process = preprocess and stretch_words
    processed_text = humanize_cadence(text, stretch=should_process)

    # 2. Output File Path
    if not output_path:
        os.makedirs("output", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join("output", f"voice_{voice_key}_{timestamp}.mp3")

    # 3. Route to Engine
    if engine == "kokoro" and KOKORO_AVAILABLE and _kokoro_instance is not None:
        # Calculate speed multiplier from rate_adj (e.g. "+0%" -> 1.0, "-10%" -> 0.90)
        speed = 0.94  # Slight 0.94x speed gives natural weight and allows words to stretch
        if "%" in rate_adj:
            try:
                pct = int(rate_adj.replace("%", "").replace("+", ""))
                speed = max(0.65, min(1.4, 0.94 + (pct / 100.0)))
            except:
                pass

        # Synthesize via Kokoro ONNX
        samples, sample_rate = _kokoro_instance.create(
            text=processed_text,
            voice=profile["voice_id"],
            speed=speed,
            lang="en-us"
        )

        # If target path is .mp3, convert via soundfile or ffmpeg
        temp_wav = output_path.replace(".mp3", ".wav")
        sf.write(temp_wav, samples, sample_rate)

        # Convert to standard MP3
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        import subprocess
        subprocess.run(
            [ffmpeg_exe, "-y", "-i", temp_wav, "-b:a", "192k", output_path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        if os.path.exists(temp_wav) and output_path.endswith(".mp3"):
            try: os.remove(temp_wav)
            except: pass

        return output_path

    # Fallback to Azure Edge Neural Engine
    communicate = edge_tts.Communicate(
        text=processed_text,
        voice=profile["voice_id"],
        rate=rate_adj or "+0%",
        pitch=pitch_adj or "+0Hz"
    )
    await communicate.save(output_path)
    return output_path
