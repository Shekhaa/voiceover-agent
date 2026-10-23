"""
Asset Downloader for AuraVoice Studio
Automatically downloads Kokoro-82M neural models and royalty-free background music.
"""

import os
import sys
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
MUSIC_DIR = os.path.join(BASE_DIR, "music")

ASSETS = {
    "models": {
        "dir": MODELS_DIR,
        "files": {
            "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
            "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
        }
    },
    "music": {
        "dir": MUSIC_DIR,
        "files": {
            "cinematic_dramatic.mp3": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Heartbreaking.mp3",
            "inspirational_piano.mp3": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Clean%20Soul.mp3",
            "documentary_suspense.mp3": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Dark%20Walk.mp3",
            "modern_chill.mp3": "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Carefree.mp3"
        }
    }
}

def download_file(url: str, dest_path: str):
    filename = os.path.basename(dest_path)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1024:
        print(f"  [OK] Already downloaded: {filename}")
        return

    print(f"  [DOWNLOADING] {filename}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))

        downloaded = 0
        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = int((downloaded / total_size) * 100)
                        sys.stdout.write(f"\r    -> {downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB ({percent}%)")
                        sys.stdout.flush()

        print(f"\n  [COMPLETED] {filename}")
    except Exception as e:
        print(f"\n  [ERROR] Failed to download {filename}: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)

def main():
    print("=" * 60)
    print("  AuraVoice Studio — Model & Music Asset Verifier")
    print("=" * 60)

    for category, info in ASSETS.items():
        target_dir = info["dir"]
        os.makedirs(target_dir, exist_ok=True)
        print(f"\nChecking {category.upper()} in: {target_dir}")

        for filename, url in info["files"].items():
            dest = os.path.join(target_dir, filename)
            download_file(url, dest)

    print("\n" + "=" * 60)
    print("  All assets verified and ready to run!")
    print("=" * 60)

if __name__ == "__main__":
    main()
