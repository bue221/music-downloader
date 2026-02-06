# src/music_downloader/zotify_downloader.py

from pathlib import Path
from typing import Optional, Callable

class ZotifyDownloader:
    def __init__(self, music_dir: Path, on_progress: Optional[Callable[[str], None]] = None):
        self._music_dir = music_dir
        self._on_progress = on_progress or (lambda x: None)

    def download_track(self, track_url: str, output_dir: Path, playlist_name: Optional[str] = None) -> dict:
        raise NotImplementedError("download_track not yet implemented")

    def download_playlist(self, playlist_url: str, output_dir: Path, playlist_name: Optional[str] = None) -> list[dict]:
        raise NotImplementedError("download_playlist not yet implemented")
