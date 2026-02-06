import pytest
from unittest.mock import MagicMock, patch
from music_downloader.spotify import SpotifyHandler
from pathlib import Path

# Mock environment variables for Spotify credentials
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "test_client_secret")

@pytest.fixture
def spotify_handler():
    # Mock dependencies for SpotifyHandler
    music_dir = Path("mock_music_dir")
    cache = MagicMock()
    cache.is_downloaded.return_value = False # Ensure not skipped by cache
    on_progress = MagicMock()
    
    handler = SpotifyHandler(music_dir=music_dir, cache=cache, on_progress=on_progress)
    
    # Mock internal calls that would go to Spotify API
    handler._extract_id = MagicMock(return_value="12345")
    handler._spotify.track = MagicMock(return_value={
        'name': 'Test Track',
        'artists': [{'name': 'Test Artist'}]
    })
    
    # Mock ZotifyDownloader
    handler._zotify_downloader = MagicMock()
    handler._zotify_downloader.download_track.return_value = {"id": "12345", "path": Path("mock_path"), "skipped": False}
    
    return handler

def test_download_track_zotify_integration_calls_zotify_downloader(spotify_handler):
    mock_track_url = "https://open.spotify.com/track/12345"
    mock_output_dir = Path("mock_output")
    mock_playlist_name = "Mock Playlist"

    # Call _download_track, which should internally call ZotifyDownloader.download_track
    result = spotify_handler._download_track(mock_track_url, mock_output_dir, mock_playlist_name)

    spotify_handler._zotify_downloader.download_track.assert_called_once_with(
        mock_track_url,
        output_dir=mock_output_dir,
        playlist_name=mock_playlist_name
    )
    assert result == {"id": "12345", "path": Path("mock_path"), "skipped": False}
