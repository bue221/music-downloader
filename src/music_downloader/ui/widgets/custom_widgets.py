"""Widgets personalizados para Music Downloader.

Este módulo contiene componentes UI reutilizables siguiendo principios SOLID.
"""

from PySide6.QtWidgets import (
    QPushButton, QFrame, QVBoxLayout, QHBoxLayout,
    QLabel, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QColor
from typing import Optional


class ModernButton(QPushButton):
    """Botón moderno con animaciones y efectos.
    
    Características:
        - Animación de hover suave
        - Efectos de sombra
        - Estilos configurables via QSS
    """
    
    def __init__(
        self,
        text: str,
        parent: Optional[QFrame] = None,
        button_type: str = "primary"
    ):
        """Inicializa el botón moderno.
        
        Args:
            text: Texto del botón
            parent: Widget padre
            button_type: Tipo de botón ('primary', 'secondary', 'danger')
        """
        super().__init__(text, parent)
        
        # Configurar tipo de botón
        if button_type == "secondary":
            self.setObjectName("secondaryButton")
        elif button_type == "danger":
            self.setObjectName("dangerButton")
        
        # Configurar cursor
        self.setCursor(Qt.PointingHandCursor)
        
        # Agregar sombra
        self._setup_shadow()
        
        # Configurar animación
        self._setup_animation()
    
    def _setup_shadow(self):
        """Configura el efecto de sombra."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
    
    def _setup_animation(self):
        """Configura animaciones de hover."""
        # La animación se puede expandir aquí si es necesario
        pass


class PanelFrame(QFrame):
    """Frame con estilo de panel/tarjeta.
    
    Características:
        - Bordes redondeados
        - Sombra sutil
        - Padding automático
    """
    
    def __init__(self, parent: Optional[QFrame] = None):
        """Inicializa el panel.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        
        # Configurar estilo
        self.setObjectName("panel")
        
        # Agregar sombra
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)


class SectionTitle(QLabel):
    """Label para títulos de sección.
    
    Características:
        - Estilo consistente
        - Tamaño de fuente apropiado
    """
    
    def __init__(self, text: str, parent: Optional[QFrame] = None):
        """Inicializa el título de sección.
        
        Args:
            text: Texto del título
            parent: Widget padre
        """
        super().__init__(text, parent)
        self.setObjectName("sectionTitle")


class StatusLabel(QLabel):
    """Label para mensajes de estado.
    
    Características:
        - Estilo secundario
        - Actualizable dinámicamente
    """
    
    def __init__(self, text: str = "", parent: Optional[QFrame] = None):
        """Inicializa el label de estado.
        
        Args:
            text: Texto inicial
            parent: Widget padre
        """
        super().__init__(text, parent)
        self.setObjectName("statusLabel")
    
    def set_status(self, message: str, status_type: str = "info"):
        """Actualiza el estado con color apropiado.
        
        Args:
            message: Mensaje a mostrar
            status_type: Tipo de estado ('info', 'success', 'warning', 'error')
        """
        self.setText(message)
        
        # Cambiar color según tipo
        colors = {
            "info": "#a0a0a0",
            "success": "#06ffa5",
            "warning": "#ffa500",
            "error": "#ff3838"
        }
        
        color = colors.get(status_type, colors["info"])
        self.setStyleSheet(f"color: {color};")


class AnimatedProgressBar(QFrame):
    """Barra de progreso personalizada con animaciones.
    
    Características:
        - Animación suave
        - Gradiente de color
        - Actualización fluida
    """
    
    def __init__(self, parent: Optional[QFrame] = None):
        """Inicializa la barra de progreso.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        
        self._progress = 0.0
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la UI de la barra."""
        self.setFixedHeight(8)
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 4px;
            }
        """)
    
    def get_progress(self) -> float:
        """Obtiene el progreso actual."""
        return self._progress
    
    def set_progress(self, value: float):
        """Establece el progreso con animación.
        
        Args:
            value: Valor de progreso (0-100)
        """
        self._progress = max(0.0, min(100.0, value))
        self.update()
    
    # Property para animaciones
    progress = Property(float, get_progress, set_progress)
    
    def animate_to(self, target_value: float, duration: int = 300):
        """Anima el progreso a un valor objetivo.
        
        Args:
            target_value: Valor objetivo (0-100)
            duration: Duración de la animación en ms
        """
        animation = QPropertyAnimation(self, b"progress")
        animation.setDuration(duration)
        animation.setStartValue(self._progress)
        animation.setEndValue(target_value)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        
        # Guardar referencia para evitar garbage collection
        self._animation = animation


class HeaderWidget(QFrame):
    """Widget de encabezado con título y subtítulo.
    
    Características:
        - Layout vertical automático
        - Estilos consistentes
    """
    
    def __init__(
        self,
        title: str,
        subtitle: str,
        parent: Optional[QFrame] = None
    ):
        """Inicializa el header.
        
        Args:
            title: Título principal
            subtitle: Subtítulo
            parent: Widget padre
        """
        super().__init__(parent)
        
        self.setObjectName("headerFrame")
        self._setup_ui(title, subtitle)
    
    def _setup_ui(self, title: str, subtitle: str):
        """Configura la UI del header."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Título
        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Subtítulo
        subtitle_label = QLabel(subtitle)
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)


class StatsWidget(QLabel):
    """Widget para mostrar estadísticas.
    
    Características:
        - Formato consistente
        - Actualización fácil
    """
    
    def __init__(self, parent: Optional[QFrame] = None):
        """Inicializa el widget de estadísticas.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.setObjectName("statsLabel")
        self.setAlignment(Qt.AlignCenter)
    
    def update_stats(self, total_songs: int, total_playlists: int):
        """Actualiza las estadísticas mostradas.
        
        Args:
            total_songs: Total de canciones
            total_playlists: Total de playlists
        """
        self.setText(
            f"Total: {total_songs} canciones | Playlists: {total_playlists}"
        )
