import pytest
from unittest.mock import MagicMock
from music_downloader.zotify_downloader import ZotifyDownloader
from pathlib import Path

@pytest.fixture
def zotify_downloader():
    music_dir = Path("mock_music_dir")
    on_progress = MagicMock()
    return ZotifyDownloader(music_dir=music_dir, on_progress=on_progress)

def test_download_track_raises_not_implemented_error(zotify_downloader):
    mock_track_url = "https://open.spotify.com/track/12345"
    mock_output_dir = Path("mock_output")
    
    with pytest.raises(NotImplementedError, match="download_track not yet implemented"):
        zotify_downloader.download_track(mock_track_url, mock_output_dir)

def test_download_playlist_raises_not_implemented_error(zotify_downloader):
    mock_playlist_url = "https://open.spotify.com/playlist/12345"
    mock_output_dir = Path("mock_output")

    with pytest.raises(NotImplementedError, match="download_playlist not yet implemented"):
        zotify_downloader.download_playlist(mock_playlist_url, mock_output_dir)
