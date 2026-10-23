"""
FastAPI Server for Voiceover Studio with Background Music & Ducking
"""

import os
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from voice_agent import VOICE_PROFILES, generate_voiceover
from humanizer import humanize_cadence
from audio_mixer import MUSIC_TRACKS, mix_voice_with_music

app = FastAPI(title="Voiceover Agent Studio")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

class VoiceRequest(BaseModel):
    text: str
    voice: str = "marcus"
    rate: str = "+0%"
    pitch: str = "+0Hz"
    music: str = "cinematic"
    music_volume: float = 0.15
    humanize: bool = True

class HumanizeRequest(BaseModel):
    text: str

@app.get("/api/voices")
def get_voices():
    return [{"key": k, **v} for k, v in VOICE_PROFILES.items()]

@app.get("/api/music")
def get_music_tracks():
    return [{"key": k, "name": v["name"], "mood": v.get("mood", "")} for k, v in MUSIC_TRACKS.items()]

@app.post("/api/humanize")
def preview_humanize(req: HumanizeRequest):
    return {"original": req.text, "humanized": humanize_cadence(req.text)}

@app.post("/api/generate")
async def generate_speech(req: VoiceRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_filename = f"voice_{req.voice}_{timestamp}.mp3"
    raw_filepath = os.path.join(OUTPUT_DIR, raw_filename)

    try:
        # 1. Synthesize Neural Speech
        await generate_voiceover(
            text=req.text,
            voice_key=req.voice,
            rate_adj=req.rate,
            pitch_adj=req.pitch,
            output_path=raw_filepath,
            preprocess=req.humanize
        )

        # 2. Master & Mix with Background Music if requested
        final_filename = raw_filename
        final_filepath = raw_filepath

        if req.music and req.music != "none":
            mixed_filename = f"mixed_{req.voice}_{req.music}_{timestamp}.mp3"
            mixed_filepath = os.path.join(OUTPUT_DIR, mixed_filename)
            mixed_result = mix_voice_with_music(
                voice_path=raw_filepath,
                music_key=req.music,
                music_volume=req.music_volume,
                output_path=mixed_filepath
            )
            if os.path.exists(mixed_result):
                final_filename = os.path.basename(mixed_result)
                final_filepath = mixed_result

        return {
            "success": True,
            "filename": final_filename,
            "audioUrl": f"/audio/{final_filename}",
            "voice": req.voice,
            "music": req.music,
            "processedText": humanize_cadence(req.text) if req.humanize else req.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
def get_audio(filename: str):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(filepath, media_type="audio/mpeg")

@app.get("/", response_class=HTMLResponse)
def get_studio_ui():
    html_file = os.path.join(os.path.dirname(__file__), "public", "index.html")
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Voiceover Studio UI Loading...</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
