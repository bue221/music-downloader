"""Ventana principal de la aplicación PySide6 - Diseño Moderno.

Layout de 2 columnas responsive y visualmente atractivo.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon
from pathlib import Path
from typing import Optional

from music_downloader.cache import DownloadCache
from .panels import DownloadPanel, ProgressPanel, SongsPanel
from .widgets.custom_widgets import HeaderWidget, StatsWidget
from .workers import DownloadWorker, CacheRefreshWorker, CacheClearWorker


# Rutas base
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
MUSIC_DIR = PROJECT_ROOT / "music"
CACHE_FILE = PROJECT_ROOT / ".downloaded.json"
STYLES_DIR = Path(__file__).parent / "styles"


class MainWindow(QMainWindow):
    """Ventana principal de Music Downloader.
    
    Diseño moderno de 2 columnas:
    - Columna izquierda: Controles de descarga y progreso
    - Columna derecha: Lista de canciones
    
    Responsabilidades:
        - Orquestar paneles y workers
        - Manejar signals y slots
        - Cargar estilos QSS
        - Gestionar estado de la aplicación
    """
    
    def __init__(self):
        """Inicializa la ventana principal."""
        super().__init__()
        
        # Inicializar componentes
        self._cache = DownloadCache(CACHE_FILE)
        self._current_worker: Optional[DownloadWorker] = None
        
        # Configurar ventana
        self._setup_window()
        
        # Cargar estilos
        self._load_styles()
        
        # Construir UI
        self._build_ui()
        
        # Cargar canciones iniciales
        self._refresh_songs()
    
    def _setup_window(self):
        """Configura las propiedades de la ventana."""
        self.setWindowTitle("Music Downloader")
        self.setMinimumSize(1100, 700)
        self.resize(1200, 750)
        
        # Configurar icono
        icon_path = STYLES_DIR.parent / "resources" / "icon.png"
        if icon_path.exists():
            from PySide6.QtGui import QIcon
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Centrar ventana
        self._center_window()
    
    def _center_window(self):
        """Centra la ventana en la pantalla."""
        screen = self.screen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def _load_styles(self):
        """Carga los estilos QSS.
        
        La paleta oscura se aplica a nivel de aplicación en launch_pyside6_gui().
        """
        qss_file = STYLES_DIR / "dark_theme.qss"
        
        try:
            with open(qss_file, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"⚠️ Archivo QSS no encontrado: {qss_file}")
        except Exception as e:
            print(f"⚠️ Error cargando estilos: {e}")
    
    def _build_ui(self):
        """Construye la interfaz de usuario con layout de 2 columnas."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal vertical
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = HeaderWidget(
            "🎵 Music Downloader",
            "Descarga música desde YouTube con estilo"
        )
        main_layout.addWidget(header)
        
        # Layout de 2 columnas
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(25)
        
        # === COLUMNA IZQUIERDA: Controles ===
        left_column = QVBoxLayout()
        left_column.setSpacing(20)
        
        # Panel de descarga
        self._download_panel = DownloadPanel()
        self._download_panel.download_requested.connect(self._on_download_requested)
        self._download_panel.file_download_requested.connect(self._on_file_download_requested)
        self._download_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        left_column.addWidget(self._download_panel)
        
        # Panel de progreso
        self._progress_panel = ProgressPanel()
        self._progress_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        left_column.addWidget(self._progress_panel)
        
        # Spacer para empujar todo hacia arriba
        left_column.addStretch()
        
        # === COLUMNA DERECHA: Lista de canciones ===
        right_column = QVBoxLayout()
        right_column.setSpacing(0)
        
        # Panel de canciones (ocupa todo el espacio vertical)
        self._songs_panel = SongsPanel(MUSIC_DIR)
        self._songs_panel.clear_cache_requested.connect(self._on_clear_cache_requested)
        self._songs_panel.delete_song_requested.connect(self._on_delete_song_requested)
        self._songs_panel.move_song_requested.connect(self._on_move_song_requested)
        self._songs_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_column.addWidget(self._songs_panel)
        
        # Agregar columnas al layout horizontal
        # Proporción 45:55 (izquierda:derecha)
        columns_layout.addLayout(left_column, 45)
        columns_layout.addLayout(right_column, 55)
        
        main_layout.addLayout(columns_layout, 1)  # Stretch factor
        
        # Footer con estadísticas
        self._stats_widget = StatsWidget()
        main_layout.addWidget(self._stats_widget)
    
    @Slot(str, str)
    def _on_download_requested(self, url: str, playlist_name: str):
        """Maneja solicitud de descarga desde URL.
        
        Args:
            url: URL de YouTube
            playlist_name: Nombre de playlist (puede estar vacío)
        """
        self._start_download([url], playlist_name)
    
    @Slot(list, str)
    def _on_file_download_requested(self, urls: list, playlist_name: str):
        """Maneja solicitud de descarga desde archivo.
        
        Args:
            urls: Lista de URLs
            playlist_name: Nombre de playlist
        """
        self._start_download(urls, playlist_name)
    
    def _start_download(self, urls: list, playlist_name: str):
        """Inicia el proceso de descarga.
        
        Args:
            urls: Lista de URLs a descargar
            playlist_name: Nombre de playlist (opcional)
        """
        # Verificar si ya hay descarga en curso
        if self._current_worker and self._current_worker.isRunning():
            QMessageBox.warning(
                self,
                "Descarga en progreso",
                "Ya hay una descarga en curso. Por favor, espera a que termine."
            )
            return
        
        # Deshabilitar controles
        self._download_panel.set_enabled(False)
        self._progress_panel.reset()
        
        # Determinar directorio de salida
        output_dir = None
        if playlist_name:
            output_dir = MUSIC_DIR / "playlists" / playlist_name
        
        # Crear y configurar worker
        self._current_worker = DownloadWorker(
            urls=urls,
            music_dir=MUSIC_DIR,
            cache=self._cache,
            output_dir=output_dir,
            playlist_name=playlist_name or None
        )
        
        # Conectar signals
        self._current_worker.progress_updated.connect(self._on_progress_updated)
        self._current_worker.status_updated.connect(self._on_status_updated)
        self._current_worker.download_complete.connect(self._on_download_complete)
        self._current_worker.download_error.connect(self._on_download_error)
        
        # Iniciar worker
        self._current_worker.start()
    
    @Slot(float)
    def _on_progress_updated(self, progress: float):
        """Actualiza la barra de progreso.
        
        Args:
            progress: Porcentaje de progreso (0-100)
        """
        self._progress_panel.update_progress(progress)
    
    @Slot(str)
    def _on_status_updated(self, message: str):
        """Actualiza el mensaje de estado.
        
        Args:
            message: Mensaje de estado
        """
        self._progress_panel.update_status(message, "info")
    
    @Slot(dict)
    def _on_download_complete(self, summary: dict):
        """Maneja la finalización de la descarga.
        
        Args:
            summary: Diccionario con resumen de descarga
        """
        # Habilitar controles
        self._download_panel.set_enabled(True)
        self._download_panel.clear_inputs()
        
        # Actualizar progreso
        self._progress_panel.update_progress(100)
        
        # Crear mensaje de resumen
        message = (
            f"✅ Descargadas: {summary['downloaded']} | "
            f"⏭️ Omitidas: {summary['skipped']}"
        )
        
        if summary['errors'] > 0:
            message += f" | ❌ Errores: {summary['errors']}"
        
        self._progress_panel.update_status(message, "success")
        
        # Refrescar lista de canciones
        self._refresh_songs()
        
        # Mostrar mensaje
        QMessageBox.information(
            self,
            "Descarga completa",
            message
        )
    
    @Slot(str)
    def _on_download_error(self, error_message: str):
        """Maneja errores de descarga.
        
        Args:
            error_message: Mensaje de error
        """
        # Habilitar controles
        self._download_panel.set_enabled(True)
        
        # Actualizar estado
        self._progress_panel.update_status(f"❌ {error_message}", "error")
        self._progress_panel.update_progress(0)
        
        # Mostrar error
        QMessageBox.critical(
            self,
            "Error de descarga",
            error_message
        )
    
    @Slot()
    def _on_clear_cache_requested(self):
        """Maneja solicitud de limpiar caché."""
        # Crear worker para limpiar caché
        worker = CacheClearWorker(self._cache)
        worker.cache_cleared.connect(self._on_cache_cleared)
        worker.clear_error.connect(self._on_cache_clear_error)
        worker.start()
        
        # Guardar referencia para evitar garbage collection
        self._cache_clear_worker = worker
    
    @Slot()
    def _on_cache_cleared(self):
        """Maneja caché limpiado exitosamente."""
        self._refresh_songs()
        
        QMessageBox.information(
            self,
            "Caché limpiado",
            "El caché ha sido limpiado exitosamente."
        )
    
    @Slot(str)
    def _on_cache_clear_error(self, error_message: str):
        """Maneja error al limpiar caché.
        
        Args:
            error_message: Mensaje de error
        """
        QMessageBox.critical(
            self,
            "Error",
            f"Error limpiando caché: {error_message}"
        )
    
    def _refresh_songs(self):
        """Refresca la lista de canciones desde el filesystem."""
        # Crear worker para cargar canciones
        worker = CacheRefreshWorker(MUSIC_DIR)
        worker.songs_loaded.connect(self._on_songs_loaded)
        worker.load_error.connect(self._on_songs_load_error)
        worker.start()
        
        # Guardar referencia
        self._refresh_worker = worker
    
    @Slot(list)
    def _on_songs_loaded(self, songs: list):
        """Maneja canciones cargadas.
        
        Args:
            songs: Lista de canciones
        """
        self._songs_panel.update_songs(songs)
        self._update_stats(songs)
    
    @Slot(str)
    def _on_songs_load_error(self, error_message: str):
        """Maneja error al cargar canciones.
        
        Args:
            error_message: Mensaje de error
        """
        print(f"⚠️ Error cargando canciones: {error_message}")
    
    def _update_stats(self, songs: list):
        """Actualiza las estadísticas.
        
        Args:
            songs: Lista de canciones
        """
        total = len(songs)
        playlists = len(set(
            s.get('playlist', '') for s in songs if s.get('playlist')
        ))
        
        self._stats_widget.update_stats(total, playlists)
    
    @Slot(str)
    def _on_delete_song_requested(self, song_id: str):
        """Maneja solicitud de eliminar canción.
        
        Args:
            song_id: ID de la canción a eliminar
        """
        try:
            import os
            
            # Obtener información de la canción
            song_info = self._cache.get(song_id)
            if not song_info:
                QMessageBox.warning(
                    self,
                    "Error",
                    "No se encontró la canción en el caché."
                )
                return
            
            # Eliminar archivo físico
            file_path = song_info.get('path')
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            
            # Eliminar del caché
            self._cache.remove(song_id)
            
            # Refrescar lista
            self._refresh_songs()
            
            QMessageBox.information(
                self,
                "Canción eliminada",
                f"'{song_info.get('title', 'Unknown')}' ha sido eliminada."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error eliminando canción: {e}"
            )
    
    @Slot(str, str)
    def _on_move_song_requested(self, song_id: str, new_playlist: str):
        """Maneja solicitud de mover canción a otra playlist.
        
        Args:
            song_id: ID de la canción
            new_playlist: Nombre de la nueva playlist
        """
        try:
            import shutil
            
            # Obtener información de la canción
            song_info = self._cache.get(song_id)
            if not song_info:
                QMessageBox.warning(
                    self,
                    "Error",
                    "No se encontró la canción en el caché."
                )
                return
            
            # Determinar nueva ruta
            old_path = Path(song_info.get('path', ''))
            if not old_path.exists():
                QMessageBox.warning(
                    self,
                    "Error",
                    "El archivo de la canción no existe."
                )
                return
            
            new_dir = MUSIC_DIR / "playlists" / new_playlist
            new_dir.mkdir(parents=True, exist_ok=True)
            new_path = new_dir / old_path.name
            
            # Mover archivo
            shutil.move(str(old_path), str(new_path))
            
            # Actualizar caché
            self._cache.update_song(
                song_id,
                path=str(new_path),
                playlist=new_playlist
            )
            
            # Refrescar lista
            self._refresh_songs()
            
            QMessageBox.information(
                self,
                "Canción movida",
                f"'{song_info.get('title', 'Unknown')}' movida a '{new_playlist}'."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error moviendo canción: {e}"
            )
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana.
        
        Args:
            event: Evento de cierre
        """
        # Cancelar descarga en curso si existe
        if self._current_worker and self._current_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Descarga en progreso",
                "Hay una descarga en progreso. ¿Deseas cancelarla y salir?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self._current_worker.cancel()
                self._current_worker.wait()  # Esperar a que termine
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def launch_pyside6_gui():
    """Función de entrada para lanzar la GUI de PySide6."""
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QPalette, QColor
    import sys
    
    app = QApplication(sys.argv)
    
    # Configurar aplicación
    app.setApplicationName("Music Downloader")
    app.setOrganizationName("MusicDownloader")
    
    # Forzar paleta oscura a nivel de aplicación (afecta modales también)
    palette = QPalette()
    
    # Colores base oscuros (Spotify)
    palette.setColor(QPalette.Window, QColor("#121212"))
    palette.setColor(QPalette.WindowText, QColor("#FFFFFF"))
    palette.setColor(QPalette.Base, QColor("#282828"))
    palette.setColor(QPalette.AlternateBase, QColor("#3E3E3E"))
    palette.setColor(QPalette.ToolTipBase, QColor("#282828"))
    palette.setColor(QPalette.ToolTipText, QColor("#FFFFFF"))
    palette.setColor(QPalette.Text, QColor("#FFFFFF"))
    palette.setColor(QPalette.Button, QColor("#3E3E3E"))
    palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))
    palette.setColor(QPalette.BrightText, QColor("#FF1168"))
    palette.setColor(QPalette.Link, QColor("#1DB954"))
    palette.setColor(QPalette.Highlight, QColor("#1DB954"))
    palette.setColor(QPalette.HighlightedText, QColor("#000000"))
    
    # Aplicar paleta a toda la aplicación
    app.setPalette(palette)
    
    # Crear y mostrar ventana
    window = MainWindow()
    window.show()
    
    # Ejecutar aplicación
    sys.exit(app.exec())
