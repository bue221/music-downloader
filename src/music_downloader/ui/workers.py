"""Workers para operaciones en segundo plano usando QThread.

Este módulo implementa workers siguiendo el patrón de Signals y Slots de Qt.
"""

from PySide6.QtCore import QThread, Signal
from pathlib import Path
from typing import Optional, List

from music_downloader.cache import DownloadCache
from music_downloader.youtube import YouTubeDownloader, YouTubeDownloadError


class DownloadWorker(QThread):
    """Worker para descargas en segundo plano.
    
    Signals:
        progress_updated: Emitido cuando hay actualización de progreso (porcentaje: float)
        status_updated: Emitido cuando cambia el estado (mensaje: str)
        download_complete: Emitido cuando termina la descarga (resumen: dict)
        download_error: Emitido cuando ocurre un error (mensaje: str)
    
    Características:
        - Ejecuta descargas sin bloquear la UI
        - Comunicación thread-safe via signals
        - Manejo robusto de errores
    """
    
    # Definir signals
    progress_updated = Signal(float)  # porcentaje
    status_updated = Signal(str)      # mensaje de estado
    download_complete = Signal(dict)  # resumen de descarga
    download_error = Signal(str)      # mensaje de error
    
    def __init__(
        self,
        urls: List[str],
        music_dir: Path,
        cache: DownloadCache,
        output_dir: Optional[Path] = None,
        playlist_name: Optional[str] = None
    ):
        """Inicializa el worker de descarga.
        
        Args:
            urls: Lista de URLs a descargar
            music_dir: Directorio base de música
            cache: Instancia del caché
            output_dir: Directorio de salida opcional
            playlist_name: Nombre de playlist opcional
        """
        super().__init__()
        
        self._urls = urls
        self._music_dir = music_dir
        self._cache = cache
        self._output_dir = output_dir
        self._playlist_name = playlist_name
        self._is_cancelled = False
    
    def run(self):
        """Ejecuta el proceso de descarga.
        
        Este método se ejecuta en un thread separado.
        """
        try:
            # Callback para progreso
            def on_progress(message: str):
                if not self._is_cancelled:
                    self.status_updated.emit(message)
            
            # Crear downloader
            downloader = YouTubeDownloader(
                music_dir=self._music_dir,
                cache=self._cache,
                on_progress=on_progress
            )
            
            all_results = []
            total_urls = len(self._urls)
            
            # Procesar cada URL
            for idx, url in enumerate(self._urls, 1):
                if self._is_cancelled:
                    self.status_updated.emit("⏸️ Descarga cancelada")
                    return
                
                # Actualizar progreso
                progress = (idx / total_urls) * 100
                self.progress_updated.emit(progress)
                
                # Descargar
                try:
                    results = downloader.download(
                        url,
                        output_dir=self._output_dir,
                        playlist_name=self._playlist_name
                    )
                    all_results.extend(results)
                except YouTubeDownloadError as e:
                    self.status_updated.emit(f"❌ Error: {e}")
                    all_results.append({
                        "error": str(e),
                        "url": url
                    })
            
            # Calcular resumen
            summary = self._calculate_summary(all_results)
            
            # Emitir señal de completado
            self.download_complete.emit(summary)
            
        except Exception as e:
            self.download_error.emit(f"Error inesperado: {e}")
    
    def _calculate_summary(self, results: List[dict]) -> dict:
        """Calcula el resumen de la descarga.
        
        Args:
            results: Lista de resultados de descarga
            
        Returns:
            Diccionario con resumen
        """
        downloaded = sum(
            1 for r in results 
            if not r.get('skipped') and not r.get('error')
        )
        skipped = sum(1 for r in results if r.get('skipped'))
        errors = sum(1 for r in results if r.get('error'))
        
        return {
            "downloaded": downloaded,
            "skipped": skipped,
            "errors": errors,
            "total": len(results)
        }
    
    def cancel(self):
        """Cancela la descarga en curso."""
        self._is_cancelled = True


class CacheRefreshWorker(QThread):
    """Worker para refrescar la lista de canciones desde el filesystem.
    
    Signals:
        songs_loaded: Emitido cuando se cargan las canciones (songs: list)
        load_error: Emitido cuando ocurre un error (mensaje: str)
    
    Características:
        - Escanea el filesystem directamente
        - Lee metadatos de archivos MP3
        - No depende del JSON
    """
    
    # Definir signals
    songs_loaded = Signal(list)  # lista de canciones
    load_error = Signal(str)     # mensaje de error
    
    def __init__(self, music_dir: Path):
        """Inicializa el worker de refresco.
        
        Args:
            music_dir: Directorio raíz de música
        """
        super().__init__()
        self._music_dir = music_dir
    
    def run(self):
        """Carga la lista de canciones desde el filesystem."""
        try:
            from music_downloader.filesystem import scan_all_songs
            songs = scan_all_songs(self._music_dir)
            self.songs_loaded.emit(songs)
        except Exception as e:
            self.load_error.emit(f"Error cargando canciones: {e}")


class CacheClearWorker(QThread):
    """Worker para limpiar el caché.
    
    Signals:
        cache_cleared: Emitido cuando se limpia el caché
        clear_error: Emitido cuando ocurre un error (mensaje: str)
    
    Características:
        - Limpia el caché de forma asíncrona
        - Previene bloqueo de UI en cachés grandes
    """
    
    # Definir signals
    cache_cleared = Signal()     # caché limpiado
    clear_error = Signal(str)    # mensaje de error
    
    def __init__(self, cache: DownloadCache):
        """Inicializa el worker de limpieza.
        
        Args:
            cache: Instancia del caché
        """
        super().__init__()
        self._cache = cache
    
    def run(self):
        """Limpia el caché."""
        try:
            self._cache.clear()
            self.cache_cleared.emit()
        except Exception as e:
            self.clear_error.emit(f"Error limpiando caché: {e}")
