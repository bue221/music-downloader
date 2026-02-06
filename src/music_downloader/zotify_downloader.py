# src/music_downloader/zotify_downloader.py

import subprocess
from pathlib import Path
from typing import Optional, Callable

class ZotifyDownloader:
    def __init__(self, music_dir: Path, on_progress: Optional[Callable[[str], None]] = None):
        self._music_dir = music_dir
        self._on_progress = on_progress or (lambda x: None)

    def download_track(self, track_url: str, output_dir: Path, playlist_name: Optional[str] = None) -> dict:
        # Build Zotify command
        cmd = [
            "zotify",
            track_url,
            "--output", str(output_dir),
            "--download-format", "mp3", # Assuming mp3 for now
            "--download-quality", "320"  # Assuming 320kbps for now
        ]
        # Zotify does not have --playlist-name for single tracks directly,
        # the output_dir handles where it goes.

        self._on_progress(f"🚀 Ejecutando Zotify: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self._on_progress(f"✅ Zotify output: {result.stdout}")
            # Zotify doesn't return the exact path directly, this is a placeholder
            # The actual path needs to be determined by Zotify's naming convention.
            return {"id": track_url, "path": output_dir / "placeholder.mp3", "skipped": False} 
        except subprocess.CalledProcessError as e:
            self._on_progress(f"❌ Error en Zotify: {e.stderr}")
            raise RuntimeError(f"Zotify download failed: {e.stderr}")

    def download_playlist(self, playlist_url: str, output_dir: Path, playlist_name: Optional[str] = None) -> list[dict]:
        # Build Zotify command for playlist
        cmd = [
            "zotify",
            playlist_url,
            "--output", str(output_dir),
            "--download-format", "mp3", # Assuming mp3 for now
            "--download-quality", "320"  # Assuming 320kbps for now
        ]
        # Zotify automatically organizes by playlist name if downloading a playlist URL

        self._on_progress(f"🚀 Ejecutando Zotify para playlist: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self._on_progress(f"✅ Zotify output: {result.stdout}")
            # Placeholder: Zotify output needs to be parsed to get individual track info
            return [{"id": playlist_url, "path": output_dir, "skipped": False}]
        except subprocess.CalledProcessError as e:
            self._on_progress(f"❌ Error en Zotify para playlist: {e.stderr}")
            raise RuntimeError(f"Zotify playlist download failed: {e.stderr}")
