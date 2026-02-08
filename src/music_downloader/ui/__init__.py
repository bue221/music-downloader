"""Módulo UI de Music Downloader con PySide6.

Arquitectura modular siguiendo principios SOLID:
- Separación de responsabilidades
- Componentes reutilizables
- Comunicación via signals/slots
- Estilos separados en QSS
"""

from .main_window import MainWindow, launch_pyside6_gui

__all__ = ['MainWindow', 'launch_pyside6_gui']
