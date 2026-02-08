"""Módulo para descarga de música desde YouTube.

Utiliza yt-dlp para descargar y convertir videos a MP3.
"""

import yt_dlp
from pathlib import Path
from typing import Callable, Optional

from .cache import DownloadCache
from .utils import sanitize_filename, ensure_directory, is_playlist_url
from .filesystem import set_video_id_to_mp3, is_song_downloaded, find_song_by_video_id


class YouTubeDownloadError(Exception):
    """Error durante la descarga desde YouTube."""
    pass


class YouTubeDownloader:
    """Gestiona descargas de música desde YouTube.
    
    Responsabilidades:
        - Descargar canciones individuales
        - Descargar playlists completas
        - Convertir a formato MP3
        - Registrar descargas en caché
    """
    
    def __init__(
        self,
        music_dir: Path,
        cache: DownloadCache,
        on_progress: Optional[Callable[[str], None]] = None
    ):
        """Inicializa el downloader.
        
        Args:
            music_dir: Directorio base para guardar música.
            cache: Instancia del caché de descargas.
            on_progress: Callback opcional para reportar progreso.
        """
        self._music_dir = music_dir
        self._cache = cache
        self._on_progress = on_progress or (lambda x: None)
        
        # Configuración base de yt-dlp
        self._base_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.youtube.com/',
            }
        }
    
    def download(
        self,
        url: str,
        output_dir: Optional[Path] = None,
        playlist_name: Optional[str] = None
    ) -> list[dict]:
        """Descarga música desde una URL de YouTube.
        
        Detecta automáticamente si es playlist o video individual.
        
        Args:
            url: URL de YouTube (video o playlist).
            output_dir: Directorio de salida forzado (opcional).
            playlist_name: Nombre de playlist forzado (opcional).
            
        Returns:
            Lista de diccionarios con info de canciones descargadas.
            
        Raises:
            YouTubeDownloadError: Si ocurre un error durante la descarga.
        """
        if is_playlist_url(url):
            return self._download_playlist(url, output_dir, playlist_name)
        return [self._download_single(url, output_dir, playlist_name)]
    
    def _download_single(
        self,
        url: str,
        output_dir: Optional[Path] = None,
        playlist_name: Optional[str] = None
    ) -> dict:
        """Descarga un video individual.
        
        Args:
            url: URL del video.
            output_dir: Directorio de salida (opcional).
            playlist_name: Nombre de la playlist (opcional).
            
        Returns:
            Diccionario con información de la canción.
        """
        # Primero extraer info para verificar caché
        try:
            info = self._extract_info(url)
        except Exception as e:
             # Si falla la extracción de info, lanzamos nuestro error personalizado
             # para que sea manejado correctamente aguas arriba
             raise YouTubeDownloadError(f"No se pudo obtener información: {e}") from e
        video_id = info.get('id', '')
        title = info.get('title', 'Unknown')
        artist = info.get('uploader', info.get('channel', 'Unknown'))
        
        # Verificar si ya está descargada usando filesystem
        if is_song_downloaded(self._music_dir, video_id):
            self._on_progress(f"⏭️  Ya descargada: {title}")
            existing_song = find_song_by_video_id(self._music_dir, video_id)
            return {
                "id": video_id,
                "title": title,
                "artist": artist,
                "skipped": True,
                "path": existing_song.get('path') if existing_song else None
            }
        
        # Determinar directorio de salida
        if output_dir is None:
            output_dir = ensure_directory(self._music_dir / "singles")
        
        # Configurar opciones de descarga
        safe_title = sanitize_filename(title)
        output_template = str(output_dir / f"{safe_title}.%(ext)s")
        
        opts = {
            **self._base_opts,
            'outtmpl': output_template,
        }
        
        # Descargar
        self._on_progress(f"⬇️  Descargando: {title}")
        
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        except Exception as e:
            raise YouTubeDownloadError(f"Error descargando {url}: {e}") from e
        
        # Guardar metadatos completos en el MP3
        final_path = output_dir / f"{safe_title}.mp3"
        from .filesystem import save_mp3_metadata
        save_mp3_metadata(final_path, title, artist, video_id)
        
        # Registrar en caché (mantener por compatibilidad)
        self._cache.register(
            song_id=video_id,
            title=title,
            artist=artist,
            source="youtube",
            path=str(final_path),
            playlist_name=playlist_name
        )
        
        self._on_progress(f"✅ Completado: {title}")
        
        return {
            "id": video_id,
            "title": title,
            "artist": artist,
            "skipped": False,
            "path": str(final_path)
        }
    
    def _download_playlist(
        self,
        url: str,
        output_dir: Optional[Path] = None,
        playlist_name: Optional[str] = None
    ) -> list[dict]:
        """Descarga una playlist completa.
        
        Args:
            url: URL de la playlist.
            output_dir: Directorio de salida forzado (opcional).
            playlist_name: Nombre de playlist forzado (opcional).
            
        Returns:
            Lista de diccionarios con info de canciones.
        """
        # Extraer info de la playlist
        playlist_info = self._extract_info(url, playlist=True)
        
        if not playlist_name:
            playlist_name = sanitize_filename(
                playlist_info.get('title', 'Unknown Playlist')
            )
        
        entries = playlist_info.get('entries', [])
        
        self._on_progress(f"📁 Playlist: {playlist_name} ({len(entries)} canciones)")
        
        # Crear directorio para la playlist
        if output_dir is None:
            playlist_dir = ensure_directory(
                self._music_dir / "playlists" / playlist_name
            )
        else:
            playlist_dir = ensure_directory(output_dir)
        
        results = []
        for entry in entries:
            if entry is None:
                continue
                
            video_url = entry.get('url') or entry.get('webpage_url')
            if not video_url:
                video_id = entry.get('id')
                if video_id:
                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                else:
                    continue
            
            try:
                result = self._download_single(
                    video_url,
                    output_dir=playlist_dir,
                    playlist_name=playlist_name
                )
                results.append(result)
            except Exception as e:
                self._on_progress(f"❌ Error ignorable: {e}")
                results.append({
                    "id": entry.get('id', 'unknown'),
                    "title": entry.get('title', 'Unknown'),
                    "error": str(e)
                })
        
        return results
    
    def _extract_info(self, url: str, playlist: bool = False) -> dict:
        """Extrae información de una URL sin descargar.
        
        Args:
            url: URL a analizar.
            playlist: Si es True, extrae info de playlist.
            
        Returns:
            Diccionario con metadata del video/playlist.
        """
        opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist' if playlist else False,
        }
        
        # Add headers if available
        if 'http_headers' in self._base_opts:
            opts['http_headers'] = self._base_opts['http_headers']
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
