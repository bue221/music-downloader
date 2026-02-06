"""Módulo para descarga de música desde Spotify.

Extrae metadata de Spotify y descarga desde YouTube.
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pathlib import Path
from typing import Callable, Optional

from .cache import DownloadCache
from .utils import sanitize_filename, ensure_directory


class SpotifyConfigError(Exception):
    """Error de configuración de Spotify."""
    pass


class SpotifyDownloadError(Exception):
    """Error durante la descarga desde Spotify."""
    pass


class SpotifyHandler:
    """Gestiona la integración con Spotify.
    
    Responsabilidades:
        - Autenticación con Spotify API
        - Extraer metadata de tracks y playlists
        - Buscar y descargar desde YouTube
    """
    
    def __init__(
        self,
        music_dir: Path,
        cache: DownloadCache,
        on_progress: Optional[Callable[[str], None]] = None
    ):
        """Inicializa el handler de Spotify.
        
        Args:
            music_dir: Directorio base para guardar música.
            cache: Instancia del caché de descargas.
            on_progress: Callback opcional para reportar progreso.
            
        Raises:
            SpotifyConfigError: Si faltan credenciales.
        """
        self._music_dir = music_dir
        self._cache = cache
        self._on_progress = on_progress or (lambda x: None)
        
        # Verificar credenciales
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise SpotifyConfigError(
                "Configura SPOTIFY_CLIENT_ID y SPOTIFY_CLIENT_SECRET en .env"
            )
        
        # Inicializar cliente de Spotify
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        self._spotify = spotipy.Spotify(auth_manager=auth_manager)
    
    def _download_track_with_zotify(self, track_url: str, output_dir: Path, playlist_name: Optional[str]) -> dict:
        """Placeholder for Zotify download integration."""
        raise AttributeError("_download_track_with_zotify not yet implemented")

    def download(
        self,
        url: str,
        output_dir: Optional[Path] = None,
        playlist_name: Optional[str] = None
    ) -> list[dict]:
        """Descarga música desde una URL de Spotify.
        
        Args:
            url: URL de Spotify (track o playlist).
            output_dir: Directorio de salida forzado (opcional).
            playlist_name: Nombre de playlist forzado (opcional).
            
        Returns:
            Lista de diccionarios con info de canciones descargadas.
        """
        if '/playlist/' in url:
            return self._download_playlist(url, output_dir, playlist_name)
        elif '/track/' in url:
            return [self._download_track(url, output_dir, playlist_name)]
        elif '/album/' in url:
            return self._download_album(url, output_dir, playlist_name)
        else:
            raise SpotifyDownloadError(f"URL no soportada: {url}")
    
    def _download_track(
        self,
        url: str,
        output_dir: Optional[Path] = None,
        playlist_name: Optional[str] = None
    ) -> dict:
        """Descarga un track individual.
        
        Args:
            url: URL del track.
            output_dir: Directorio de salida (opcional).
            playlist_name: Nombre de la playlist (opcional).
            
        Returns:
            Diccionario con información del track.
        """
        # Extraer ID del track
        track_id = self._extract_id(url, 'track')
        
        # Verificar caché
        if self._cache.is_downloaded(f"spotify:{track_id}"):
            path = self._cache.get_path(f"spotify:{track_id}")
            self._on_progress(f"⏭️  Ya descargada (Spotify)")
            return {"id": track_id, "skipped": True, "path": path}
        
        # Obtener metadata de Spotify
        track = self._spotify.track(track_id)
        title = track['name']
        artists = ', '.join(a['name'] for a in track['artists'])
        
        self._on_progress(f"🎧 Descargando con Zotify: {artists} - {title}")
        
        # Llamar al método de descarga de Zotify
        result = self._download_track_with_zotify(
            url,
            output_dir=output_dir,
            playlist_name=playlist_name
        )
        
        # Registrar con ID de Spotify también
        if not result.get('skipped') and result.get('path'):
            self._cache.register(
                song_id=f"spotify:{track_id}",
                title=title,
                artist=artists,
                source="spotify",
                path=result['path'],
                playlist_name=playlist_name
            )
        
        return result
    
    def _download_playlist(
        self,
        url: str,
        output_dir: Optional[Path] = None,
        playlist_name: Optional[str] = None
    ) -> list[dict]:
        """Descarga una playlist completa de Spotify.
        
        Args:
            url: URL de la playlist.
            output_dir: Directorio de salida forzado (opcional).
            playlist_name: Nombre de playlist forzado (opcional).
            
        Returns:
            Lista de diccionarios con info de canciones.
        """
        playlist_id = self._extract_id(url, 'playlist')
        playlist = self._spotify.playlist(playlist_id)
        
        if not playlist_name:
            playlist_name = sanitize_filename(playlist['name'])
        
        self._on_progress(
            f"📁 Playlist Spotify: {playlist_name} "
            f"({playlist['tracks']['total']} canciones)"
        )
        
        # Crear directorio para la playlist
        if output_dir is None:
            playlist_dir = ensure_directory(
                self._music_dir / "playlists" / playlist_name
            )
        else:
            playlist_dir = ensure_directory(output_dir)
        
        results = []
        tracks = playlist['tracks']
        
        while tracks:
            for item in tracks['items']:
                track = item.get('track')
                if not track:
                    continue
                
                track_url = track['external_urls'].get('spotify')
                if track_url:
                    try:
                        result = self._download_track(
                            track_url,
                            output_dir=playlist_dir,
                            playlist_name=playlist_name
                        )
                        results.append(result)
                    except Exception as e:
                        self._on_progress(f"❌ Error: {e}")
                        results.append({
                            "id": track.get('id', 'unknown'),
                            "title": track.get('name', 'Unknown'),
                            "error": str(e)
                        })
            
            # Siguiente página
            if tracks['next']:
                tracks = self._spotify.next(tracks)
            else:
                break
        
        return results
    
    def _download_album(
        self,
        url: str,
        output_dir: Optional[Path] = None,
        playlist_name: Optional[str] = None
    ) -> list[dict]:
        """Descarga un álbum completo.
        
        Args:
            url: URL del álbum.
            output_dir: Directorio de salida forzado (opcional).
            playlist_name: Nombre de playlist forzado (opcional).
            
        Returns:
            Lista de diccionarios con info de canciones.
        """
        album_id = self._extract_id(url, 'album')
        album = self._spotify.album(album_id)
        
        if not playlist_name:
            fixed_name = sanitize_filename(album['name'])
            artist = album['artists'][0]['name']
            playlist_name = f"{artist} - {fixed_name}"
            
        self._on_progress(
            f"💿 Álbum: {playlist_name} "
            f"({album['total_tracks']} canciones)"
        )
        
        # Crear directorio para el álbum
        if output_dir is None:
            album_dir = ensure_directory(
                self._music_dir / "playlists" / playlist_name
            )
        else:
            album_dir = ensure_directory(output_dir)
        
        results = []
        for track in album['tracks']['items']:
            track_url = f"https://open.spotify.com/track/{track['id']}"
            try:
                result = self._download_track(
                    track_url,
                    output_dir=album_dir,
                    playlist_name=album_name
                )
                results.append(result)
            except Exception as e:
                self._on_progress(f"❌ Error: {e}")
                results.append({
                    "id": track.get('id', 'unknown'),
                    "title": track.get('name', 'Unknown'),
                    "error": str(e)
                })
        
        return results
    
    def _extract_id(self, url: str, resource_type: str) -> str:
        """Extrae el ID de un recurso de Spotify.
        
        Args:
            url: URL de Spotify.
            resource_type: Tipo de recurso ('track', 'playlist', 'album').
            
        Returns:
            ID del recurso.
            
        Raises:
            SpotifyDownloadError: Si no se puede extraer el ID.
        """
        import re
        
        pattern = rf'{resource_type}/([a-zA-Z0-9]+)'
        match = re.search(pattern, url)
        
        if not match:
            raise SpotifyDownloadError(
                f"No se pudo extraer ID de {resource_type} de: {url}"
            )
        
        return match.group(1)

