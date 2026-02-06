"""Utilidades comunes para el proyecto.

Funciones de ayuda para formateo, validación y operaciones comunes.
"""

import re
from pathlib import Path


def sanitize_filename(name: str) -> str:
    """Limpia un nombre para usarlo como nombre de archivo.
    
    Remueve caracteres no permitidos en sistemas de archivos y
    normaliza espacios.
    
    Args:
        name: Nombre original.
        
    Returns:
        Nombre sanitizado seguro para el sistema de archivos.
    """
    # Remover caracteres no permitidos
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
    # Reemplazar múltiples espacios por uno solo
    sanitized = re.sub(r'\s+', ' ', sanitized)
    # Remover espacios al inicio y final
    sanitized = sanitized.strip()
    # Limitar longitud
    return sanitized[:200] if len(sanitized) > 200 else sanitized


def ensure_directory(path: Path) -> Path:
    """Asegura que un directorio exista.
    
    Args:
        path: Ruta del directorio.
        
    Returns:
        La misma ruta para encadenar operaciones.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_duration(seconds: int) -> str:
    """Formatea duración en segundos a formato legible.
    
    Args:
        seconds: Duración en segundos.
        
    Returns:
        String formateado (ej: "3:45" o "1:02:30").
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def extract_video_id(url: str) -> str | None:
    """Extrae el ID del video de una URL de YouTube.
    
    Args:
        url: URL de YouTube.
        
    Returns:
        ID del video o None si no se puede extraer.
    """
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def is_playlist_url(url: str) -> bool:
    """Determina si una URL es de una playlist.
    
    Args:
        url: URL a verificar.
        
    Returns:
        True si es una playlist, False en caso contrario.
    """
    return 'list=' in url or '/playlist/' in url
