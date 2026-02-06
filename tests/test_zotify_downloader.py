import pytest
from unittest.mock import MagicMock, patch
import subprocess
from music_downloader.zotify_downloader import ZotifyDownloader
from pathlib import Path

@pytest.fixture
def zotify_downloader():
    music_dir = Path("mock_music_dir")
    on_progress = MagicMock()
    return ZotifyDownloader(music_dir=music_dir, on_progress=on_progress)

def test_download_track_raises_runtime_error(zotify_downloader):
    mock_track_url = "https://open.spotify.com/track/12345"
    mock_output_dir = Path("mock_output")
    
    with patch("music_downloader.zotify_downloader.subprocess.run") as mock_subprocess_run:
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["zotify"], stderr="Error from zotify")
        with pytest.raises(RuntimeError, match="Zotify download failed"):
            zotify_downloader.download_track(mock_track_url, mock_output_dir)

def test_download_playlist_raises_not_implemented_error(zotify_downloader):
    mock_playlist_url = "https://open.spotify.com/playlist/12345"
    mock_output_dir = Path("mock_output")

    with pytest.raises(NotImplementedError, match="download_playlist not yet implemented"):
        zotify_downloader.download_playlist(mock_playlist_url, mock_output_dir)

def test_zotify_download_track_calls_subprocess(zotify_downloader):
    mock_track_url = "https://open.spotify.com/track/12345"
    mock_output_dir = Path("mock_output")
    mock_playlist_name = "Mock Playlist"

    with patch("music_downloader.zotify_downloader.subprocess.run") as mock_subprocess_run:
        mock_subprocess_run.return_value = MagicMock(returncode=0, stdout="Mock Zotify Output")
        
        zotify_downloader.download_track(mock_track_url, mock_output_dir, mock_playlist_name)
        
        mock_subprocess_run.assert_called_once()
        args = mock_subprocess_run.call_args[0][0]
        
        assert "zotify" in args
        assert mock_track_url in args
        assert str(mock_output_dir) in args
        assert "--download-format" in args
        assert "mp3" in args
        assert "--download-quality" in args
        assert "320" in args

def test_zotify_download_track_raises_runtime_error_on_zotify_failure(zotify_downloader):
    mock_track_url = "https://open.spotify.com/track/12345"
    mock_output_dir = Path("mock_output")
    mock_playlist_name = "Mock Playlist"

    with patch("music_downloader.zotify_downloader.subprocess.run") as mock_subprocess_run:
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(returncode=1, cmd=["zotify"], stderr="Error from zotify")
        
        with pytest.raises(RuntimeError, match="Zotify download failed: Error from zotify"):
            zotify_downloader.download_track(mock_track_url, mock_output_dir, mock_playlist_name)
