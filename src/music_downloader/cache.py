"""Módulo de caché para controlar descargas duplicadas.

Este módulo maneja la persistencia de las canciones descargadas,
evitando re-descargas innecesarias.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class DownloadCache:
    """Gestiona el registro de canciones descargadas.
    
    Responsabilidades:
        - Persistir metadata de canciones descargadas
        - Verificar si una canción ya fue descargada
        - Listar canciones en caché
    """
    
    def __init__(self, cache_file: Path):
        """Inicializa el caché.
        
        Args:
            cache_file: Ruta al archivo JSON de caché.
        """
        self._cache_file = cache_file
        self._data = self._load()
    
    def _load(self) -> dict:
        """Carga el caché desde disco."""
        if self._cache_file.exists():
            try:
                with open(self._cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"songs": {}}
        return {"songs": {}}
    
    def _save(self) -> None:
        """Persiste el caché a disco."""
        with open(self._cache_file, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
    
    def is_downloaded(self, song_id: str) -> bool:
        """Verifica si una canción ya fue descargada.
        
        Args:
            song_id: Identificador único de la canción (video_id o track_id).
            
        Returns:
            True si ya está en caché, False en caso contrario.
        """
        return song_id in self._data["songs"]
    
    def get_path(self, song_id: str) -> Optional[str]:
        """Obtiene la ruta de una canción descargada.
        
        Args:
            song_id: Identificador único de la canción.
            
        Returns:
            Ruta al archivo si existe, None en caso contrario.
        """
        song = self._data["songs"].get(song_id)
        return song.get("path") if song else None
    
    def register(
        self,
        song_id: str,
        title: str,
        artist: str,
        source: str,
        path: str,
        playlist_name: Optional[str] = None
    ) -> None:
        """Registra una canción como descargada.
        
        Args:
            song_id: Identificador único de la canción.
            title: Título de la canción.
            artist: Nombre del artista.
            source: Plataforma de origen ('youtube' o 'spotify').
            path: Ruta donde se guardó el archivo.
            playlist_name: Nombre de la playlist (opcional).
        """
        self._data["songs"][song_id] = {
            "title": title,
            "artist": artist,
            "source": source,
            "path": path,
            "playlist": playlist_name,
            "downloaded_at": datetime.now().isoformat()
        }
        self._save()
    
    def list_songs(self) -> list[dict]:
        """Lista todas las canciones descargadas.
        
        Returns:
            Lista de diccionarios con información de cada canción.
        """
        return [
            {"id": song_id, **data}
            for song_id, data in self._data["songs"].items()
        ]
    
    def clear(self) -> None:
        """Limpia todo el caché."""
        self._data = {"songs": {}}
        self._save()
    
    def get(self, song_id: str) -> Optional[dict]:
        """Obtiene información de una canción por ID.
        
        Args:
            song_id: Identificador único de la canción.
            
        Returns:
            Diccionario con información de la canción o None si no existe.
        """
        return self._data["songs"].get(song_id)
    
    def remove(self, song_id: str) -> bool:
        """Elimina una canción del caché.
        
        Args:
            song_id: Identificador único de la canción.
            
        Returns:
            True si se eliminó, False si no existía.
        """
        if song_id in self._data["songs"]:
            del self._data["songs"][song_id]
            self._save()
            return True
        return False
    
    def update_song(
        self,
        song_id: str,
        path: Optional[str] = None,
        playlist: Optional[str] = None
    ) -> bool:
        """Actualiza información de una canción.
        
        Args:
            song_id: Identificador único de la canción.
            path: Nueva ruta del archivo (opcional).
            playlist: Nueva playlist (opcional).
            
        Returns:
            True si se actualizó, False si no existía.
        """
        if song_id not in self._data["songs"]:
            return False
        
        if path is not None:
            self._data["songs"][song_id]["path"] = path
        
        if playlist is not None:
            self._data["songs"][song_id]["playlist"] = playlist
        
        self._save()
        return True
