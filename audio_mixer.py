"""
Audio Mixer with Auto-Ducking and Background Music
Uses FFmpeg to master voiceover speech with cinematic royalty-free music.
"""

import os
import subprocess
import imageio_ffmpeg

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")

MUSIC_TRACKS = {
    "none": {"name": "No Background Music", "file": None},
    "cinematic": {
        "name": "Dramatic Cinematic (Hans Zimmer Style)",
        "file": os.path.join(MUSIC_DIR, "cinematic_dramatic.mp3"),
        "default_volume": 0.14,
        "mood": "Intense, dramatic hooks, mystery, film trailers"
    },
    "inspirational": {
        "name": "Emotional & Uplifting Piano",
        "file": os.path.join(MUSIC_DIR, "inspirational_piano.mp3"),
        "default_volume": 0.16,
        "mood": "Storytelling, motivation, real-life journeys, deep reflections"
    },
    "suspense": {
        "name": "Dark Ambient & True Crime Tension",
        "file": os.path.join(MUSIC_DIR, "documentary_suspense.mp3"),
        "default_volume": 0.15,
        "mood": "True crime, conspiracy, unsolved mysteries, thrilling hooks"
    },
    "chill": {
        "name": "Modern Chill & Tech Explainer",
        "file": os.path.join(MUSIC_DIR, "modern_chill.mp3"),
        "default_volume": 0.12,
        "mood": "Product demos, YouTube tutorials, SaaS guides, vlogs"
    }
}

def get_audio_duration(file_path: str) -> float:
    """
    Returns the duration of an audio file in seconds using ffmpeg.
    """
    cmd = [
        FFMPEG_EXE, "-i", file_path,
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True, errors="replace")
    import re
    match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", result.stderr)
    if match:
        h, m, s = match.groups()
        return int(h) * 3600 + int(m) * 60 + float(s)
    return 10.0 # fallback

def mix_voice_with_music(
    voice_path: str,
    music_key: str = "cinematic",
    music_volume: float = 0.15,
    output_path: str = None
) -> str:
    """
    Mixes voiceover with background music, applying auto-ducking and fade-out.
    """
    track_info = MUSIC_TRACKS.get(music_key, MUSIC_TRACKS["none"])
    if not track_info.get("file") or not os.path.exists(track_info["file"]):
        return voice_path # Return voiceover without music if none selected

    if not output_path:
        base, ext = os.path.splitext(voice_path)
        output_path = f"{base}_mixed.mp3"

    voice_duration = get_audio_duration(voice_path)
    total_duration = voice_duration + 1.5  # 1.5s outro music tail
    fade_start = max(0.5, total_duration - 2.0)

    # FFmpeg complex filter:
    # 1. Scale background music volume (e.g. 0.15)
    # 2. Fade in at 0s, fade out at end of speech
    # 3. Mix voice (at full 1.0 volume) and ducked music together
    filter_graph = (
        f"[1:a]volume={music_volume:.2f},atrim=0:{total_duration:.2f},"
        f"afade=t=in:st=0:d=0.5,afade=t=out:st={fade_start:.2f}:d=2.0[bgm];"
        f"[0:a]volume=1.1[voice];"
        f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[out]"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", voice_path,
        "-i", track_info["file"],
        "-filter_complex", filter_graph,
        "-map", "[out]",
        "-ac", "2",
        "-ar", "44100",
        "-b:a", "192k",
        output_path
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors="replace")
    if proc.returncode != 0:
        print(f"[MIXER ERROR] {proc.stderr}")
        return voice_path # fallback to raw voice if mixing fails

    return output_path
