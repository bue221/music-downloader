"""Paneles modulares de la interfaz - Versión mejorada.

Cada panel es un componente independiente con responsabilidad única (SOLID).
Incluye gestión de playlists y operaciones sobre canciones.
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLineEdit,
    QListWidget, QFileDialog, QMessageBox, QProgressBar,
    QComboBox, QMenu, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QCursor
from typing import Optional
from pathlib import Path

from .widgets.custom_widgets import (
    ModernButton, PanelFrame, SectionTitle,
    StatusLabel, StatsWidget
)
from music_downloader.filesystem import scan_playlists, scan_all_songs, truncate_text


class DownloadPanel(PanelFrame):
    """Panel para configurar y iniciar descargas.
    
    Signals:
        download_requested: Emitido cuando se solicita descarga (url: str, playlist_name: str)
        file_download_requested: Emitido para descarga desde archivo (urls: list, playlist_name: str)
    
    Responsabilidades:
        - Capturar URL de entrada
        - Capturar nombre de playlist
        - Validar entrada
        - Emitir señales de descarga
    """
    
    # Signals
    download_requested = Signal(str, str)  # url, playlist_name
    file_download_requested = Signal(list, str)  # urls, playlist_name
    
    def __init__(self, parent: Optional[QFrame] = None):
        """Inicializa el panel de descarga.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del panel."""
        layout = QVBoxLayout(self)
        layout.setSpacing(18)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title = SectionTitle("📥 Nueva Descarga")
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Input de URL
        url_label = StatusLabel("URL de YouTube:")
        self._url_input = QLineEdit()
        self._url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")
        self._url_input.setMinimumHeight(50)
        
        layout.addWidget(url_label)
        layout.addWidget(self._url_input)
        
        # Input de nombre de playlist
        name_label = StatusLabel("Nombre de Playlist (opcional):")
        self._playlist_input = QLineEdit()
        self._playlist_input.setPlaceholderText("Mi Playlist Favorita")
        self._playlist_input.setMinimumHeight(50)
        
        layout.addWidget(name_label)
        layout.addWidget(self._playlist_input)
        
        layout.addSpacing(10)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self._download_btn = ModernButton("⬇️ Descargar", button_type="primary")
        self._download_btn.clicked.connect(self._on_download_clicked)
        self._download_btn.setMinimumHeight(52)
        
        self._file_btn = ModernButton("📁 Archivo", button_type="secondary")
        self._file_btn.clicked.connect(self._on_file_clicked)
        self._file_btn.setMinimumHeight(52)
        
        buttons_layout.addWidget(self._download_btn)
        buttons_layout.addWidget(self._file_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_download_clicked(self):
        """Maneja el clic en el botón de descarga."""
        url = self._url_input.text().strip()
        
        if not url:
            QMessageBox.warning(
                self,
                "URL requerida",
                "Por favor, ingresa una URL de YouTube."
            )
            return
        
        playlist_name = self._playlist_input.text().strip()
        self.download_requested.emit(url, playlist_name)
    
    def _on_file_clicked(self):
        """Maneja el clic en el botón de archivo."""
        playlist_name = self._playlist_input.text().strip()
        
        if not playlist_name:
            QMessageBox.warning(
                self,
                "Nombre requerido",
                "Por favor, ingresa un nombre para la playlist antes de seleccionar el archivo."
            )
            return
        
        # Abrir diálogo de archivo
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de URLs",
            "",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]
                
                if urls:
                    self._url_input.setText(f"{len(urls)} URLs cargadas")
                    self.file_download_requested.emit(urls, playlist_name)
                else:
                    QMessageBox.warning(
                        self,
                        "Archivo vacío",
                        "El archivo no contiene URLs."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error leyendo archivo: {e}"
                )
    
    def clear_inputs(self):
        """Limpia los campos de entrada."""
        self._url_input.clear()
    
    def set_enabled(self, enabled: bool):
        """Habilita o deshabilita los controles.
        
        Args:
            enabled: True para habilitar, False para deshabilitar
        """
        self._download_btn.setEnabled(enabled)
        self._file_btn.setEnabled(enabled)
        self._url_input.setEnabled(enabled)
        self._playlist_input.setEnabled(enabled)


class ProgressPanel(PanelFrame):
    """Panel para mostrar el progreso de descarga.
    
    Responsabilidades:
        - Mostrar estado actual
        - Mostrar barra de progreso
        - Actualizar en tiempo real
    """
    
    def __init__(self, parent: Optional[QFrame] = None):
        """Inicializa el panel de progreso.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del panel."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label de estado
        self._status_label = StatusLabel("Listo para descargar")
        layout.addWidget(self._status_label)
        
        # Barra de progreso
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setMinimumHeight(8)
        
        layout.addWidget(self._progress_bar)
    
    def update_status(self, message: str, status_type: str = "info"):
        """Actualiza el mensaje de estado.
        
        Args:
            message: Mensaje a mostrar
            status_type: Tipo de estado ('info', 'success', 'warning', 'error')
        """
        self._status_label.set_status(message, status_type)
    
    def update_progress(self, value: float):
        """Actualiza la barra de progreso.
        
        Args:
            value: Valor de progreso (0-100)
        """
        self._progress_bar.setValue(int(value))
    
    def reset(self):
        """Resetea el panel a su estado inicial."""
        self._status_label.set_status("Listo para descargar", "info")
        self._progress_bar.setValue(0)


class SongsPanel(PanelFrame):
    """Panel para mostrar y gestionar canciones descargadas.
    
    Signals:
        clear_cache_requested: Emitido cuando se solicita limpiar caché
        delete_song_requested: Emitido cuando se solicita eliminar canción (song_id: str)
        move_song_requested: Emitido cuando se solicita mover canción (song_id: str, new_playlist: str)
    
    Responsabilidades:
        - Mostrar lista de canciones
        - Filtrar por playlist
        - Permitir operaciones sobre canciones
        - Actualizar estadísticas
    """
    
    # Signals
    clear_cache_requested = Signal()
    delete_song_requested = Signal(str)  # song_id
    move_song_requested = Signal(str, str)  # song_id, new_playlist
    
    def __init__(self, music_dir: Path, parent: Optional[QFrame] = None):
        """Inicializa el panel de canciones.
        
        Args:
            music_dir: Directorio raíz de música
            parent: Widget padre
        """
        super().__init__(parent)
        self._music_dir = music_dir
        self._songs_data = []  # Almacenar datos completos
        self._playlist_mapping = {}  # Mapeo de nombres truncados a completos
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del panel."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header con título, filtro y botón
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        title = SectionTitle("📚 Biblioteca")
        header_layout.addWidget(title)
        
        # Filtro de playlist
        self._playlist_filter = QComboBox()
        self._playlist_filter.addItem("Todas las playlists")
        self._playlist_filter.currentTextChanged.connect(self._on_filter_changed)
        self._playlist_filter.setMinimumWidth(180)
        header_layout.addWidget(self._playlist_filter)
        
        header_layout.addStretch()
        
        # Botón de limpiar caché más pequeño
        clear_btn = ModernButton("🗑️", button_type="danger")
        clear_btn.setObjectName("smallButton")
        clear_btn.clicked.connect(self._on_clear_clicked)
        clear_btn.setFixedWidth(40)
        clear_btn.setFixedHeight(40)
        clear_btn.setToolTip("Limpiar caché")
        
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Lista de canciones
        self._songs_list = QListWidget()
        self._songs_list.setMinimumHeight(200)
        self._songs_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._songs_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._songs_list)
    
    def _show_context_menu(self, position):
        """Muestra menú contextual para operaciones sobre canciones.
        
        Args:
            position: Posición del cursor
        """
        item = self._songs_list.itemAt(position)
        if not item:
            return
        
        # Obtener índice y datos de la canción
        index = self._songs_list.row(item)
        if index >= len(self._songs_data):
            return
        
        song = self._songs_data[index]
        song_id = song.get('id', '')
        
        # Crear menú
        menu = QMenu(self)
        
        # Acción: Eliminar
        delete_action = QAction("🗑️ Eliminar canción", self)
        delete_action.triggered.connect(lambda: self._on_delete_song(song_id, song))
        menu.addAction(delete_action)
        
        # Acción: Mover a playlist
        move_menu = menu.addMenu("📁 Mover a playlist")
        
        # Obtener playlists disponibles
        playlists = self._get_available_playlists()
        current_playlist = song.get('playlist', '')
        
        for playlist in playlists:
            if playlist != current_playlist:
                action = QAction(playlist, self)
                action.triggered.connect(
                    lambda checked, p=playlist, sid=song_id: self._on_move_song(sid, p)
                )
                move_menu.addAction(action)
        
        # Mostrar menú
        menu.exec(QCursor.pos())
    
    def _get_available_playlists(self) -> list:
        """Obtiene lista de playlists disponibles del filesystem.
        
        Returns:
            Lista de nombres de playlists
        """
        return scan_playlists(self._music_dir)
    
    def _on_delete_song(self, song_id: str, song: dict):
        """Maneja la eliminación de una canción.
        
        Args:
            song_id: ID de la canción
            song: Datos de la canción
        """
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Eliminar '{song.get('title', 'Unknown')}'?\n\n"
            "Esto eliminará el archivo del disco.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_song_requested.emit(song_id)
    
    def _on_move_song(self, song_id: str, new_playlist: str):
        """Maneja el movimiento de una canción.
        
        Args:
            song_id: ID de la canción
            new_playlist: Nombre de la nueva playlist
        """
        self.move_song_requested.emit(song_id, new_playlist)
    
    def _on_filter_changed(self, playlist_name: str):
        """Maneja el cambio de filtro de playlist.
        
        Args:
            playlist_name: Nombre de la playlist seleccionada
        """
        self._apply_filter(playlist_name)
    
    def _apply_filter(self, playlist_name: str):
        """Aplica filtro a la lista de canciones.
        
        Args:
            playlist_name: Nombre de la playlist ("Todas" para mostrar todas)
        """
        self._songs_list.clear()
        
        if not self._songs_data:
            self._songs_list.addItem("  No hay canciones descargadas")
            return
        
        filtered_songs = self._songs_data
        if playlist_name != "Todas":
            filtered_songs = [
                s for s in self._songs_data 
                if s.get('playlist') == playlist_name
            ]
        
        if not filtered_songs:
            self._songs_list.addItem(f"  No hay canciones en '{playlist_name}'")
            return
        
        for song in filtered_songs:
            artist = song.get('artist', 'Unknown')
            title = song.get('title', 'Unknown')
            playlist = f" • {song.get('playlist')}" if song.get('playlist') else ""
            
            self._songs_list.addItem(f"  🎵 {artist} - {title}{playlist}")
    
    def _on_clear_clicked(self):
        """Maneja el clic en limpiar caché."""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Limpiar el caché?\n\n"
            "Esto no eliminará los archivos, solo el registro.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.clear_cache_requested.emit()
    
    def update_songs(self, songs: list):
        """Actualiza la lista de canciones.
        
        Args:
            songs: Lista de diccionarios con info de canciones
        """
        self._songs_data = songs
        
        # Actualizar filtro de playlists
        current_filter = self._playlist_filter.currentText()
        self._playlist_filter.clear()
        self._playlist_filter.addItem("Todas")
        
        playlists = self._get_available_playlists()
        self._playlist_mapping = {}  # Limpiar mapeo anterior
        for playlist in playlists:
            # Truncar nombres largos
            display_name = truncate_text(playlist, 25)
            self._playlist_mapping[display_name] = playlist  # Guardar mapeo
            self._playlist_filter.addItem(display_name)
        
        # Restaurar filtro si existe
        index = self._playlist_filter.findText(current_filter)
        if index >= 0:
            self._playlist_filter.setCurrentIndex(index)
        else:
            self._apply_filter("Todas")
    
    def get_songs_count(self) -> int:
        """Obtiene el número total de canciones.
        
        Returns:
            Número de canciones
        """
        return len(self._songs_data)
