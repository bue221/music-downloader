"""Utilidades para escanear el sistema de archivos de música.

Proporciona funciones para descubrir playlists y canciones
directamente del sistema de archivos, usando metadatos MP3.
"""

from pathlib import Path
from typing import List, Dict, Optional
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TXXX
from mutagen.mp3 import MP3
import os


def get_video_id_from_mp3(file_path: Path) -> Optional[str]:
    """Obtiene el video_id almacenado en los metadatos del MP3.
    
    Args:
        file_path: Ruta al archivo MP3
        
    Returns:
        Video ID si existe, None en caso contrario
    """
    try:
        audio = ID3(str(file_path))
        # Buscar en campos TXXX (user-defined text)
        for frame in audio.getall('TXXX'):
            if frame.desc == 'video_id':
                return frame.text[0] if frame.text else None
        return None
    except Exception:
        return None


def set_video_id_to_mp3(file_path: Path, video_id: str) -> bool:
    """Guarda el video_id en los metadatos del MP3.
    
    Args:
        file_path: Ruta al archivo MP3
        video_id: ID del video de YouTube
        
    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        audio = ID3(str(file_path))
        # Agregar o actualizar campo TXXX con video_id
        audio.add(TXXX(encoding=3, desc='video_id', text=video_id))
        audio.save()
        return True
    except Exception as e:
        print(f"Error guardando video_id: {e}")
        return False


def save_mp3_metadata(file_path: Path, title: str, artist: str, video_id: str) -> bool:
    """Guarda metadatos completos en el MP3.
    
    Args:
        file_path: Ruta al archivo MP3
        title: Título de la canción
        artist: Artista
        video_id: ID del video de YouTube
        
    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        # Guardar tags estándar con EasyID3
        audio = EasyID3(str(file_path))
        audio['title'] = title
        audio['artist'] = artist
        audio.save()
        
        # Guardar video_id
        set_video_id_to_mp3(file_path, video_id)
        
        return True
    except Exception as e:
        print(f"Error guardando metadatos: {e}")
        # Intentar crear tags si no existen
        try:
            from mutagen.id3 import ID3NoHeaderError
            audio = MP3(str(file_path))
            audio.add_tags()
            audio.save()
            # Reintentar
            return save_mp3_metadata(file_path, title, artist, video_id)
        except Exception as e2:
            print(f"Error creando tags: {e2}")
            return False


def get_mp3_metadata(file_path: Path) -> Dict[str, str]:
    """Obtiene metadatos de un archivo MP3 usando el nombre del archivo.
    
    Args:
        file_path: Ruta al archivo MP3
        
    Returns:
        Diccionario con metadatos (title, artist, video_id, etc.)
    """
    metadata = {
        "title": "Unknown",
        "artist": "Unknown",
        "album": None,
        "video_id": None,
        "path": str(file_path),
        "filename": file_path.name
    }
    
    # Extraer del nombre del archivo
    # Formato esperado: "Artist - Title.mp3"
    filename = file_path.stem
    
    if " - " in filename:
        artist, title = filename.split(" - ", 1)
        metadata['artist'] = artist.strip()
        metadata['title'] = title.strip()
    else:
        metadata['title'] = filename
    
    # Intentar leer video_id de metadatos
    try:
        metadata['video_id'] = get_video_id_from_mp3(file_path)
    except Exception:
        pass
    
    return metadata


def scan_playlists(music_dir: Path) -> List[str]:
    """Escanea el directorio de música para encontrar playlists.
    
    Args:
        music_dir: Directorio raíz de música
        
    Returns:
        Lista de nombres de playlists encontradas
    """
    playlists = []
    
    # Buscar en music/playlists/
    playlists_dir = music_dir / "playlists"
    if playlists_dir.exists() and playlists_dir.is_dir():
        for item in playlists_dir.iterdir():
            if item.is_dir():
                # Verificar si tiene archivos MP3
                mp3_files = list(item.glob("*.mp3"))
                if mp3_files:
                    playlists.append(item.name)
    
    return sorted(playlists)


def scan_songs_in_playlist(music_dir: Path, playlist_name: str) -> List[Dict[str, str]]:
    """Escanea canciones en una playlist específica usando metadatos.
    
    Args:
        music_dir: Directorio raíz de música
        playlist_name: Nombre de la playlist
        
    Returns:
        Lista de diccionarios con información de canciones
    """
    songs = []
    playlist_dir = music_dir / "playlists" / playlist_name
    
    if not playlist_dir.exists():
        return songs
    
    for mp3_file in playlist_dir.glob("*.mp3"):
        metadata = get_mp3_metadata(mp3_file)
        metadata['playlist'] = playlist_name
        metadata['id'] = metadata.get('video_id', mp3_file.stem)  # Usar video_id o filename como ID
        songs.append(metadata)
    
    return songs


def scan_all_songs(music_dir: Path) -> List[Dict[str, str]]:
    """Escanea todas las canciones en el directorio de música.
    
    Args:
        music_dir: Directorio raíz de música
        
    Returns:
        Lista de diccionarios con información de todas las canciones
    """
    all_songs = []
    
    # Escanear playlists
    playlists = scan_playlists(music_dir)
    for playlist in playlists:
        songs = scan_songs_in_playlist(music_dir, playlist)
        all_songs.extend(songs)
    
    # Escanear singles (music/singles/)
    singles_dir = music_dir / "singles"
    if singles_dir.exists() and singles_dir.is_dir():
        for mp3_file in singles_dir.glob("*.mp3"):
            metadata = get_mp3_metadata(mp3_file)
            metadata['playlist'] = None
            metadata['id'] = metadata.get('video_id', mp3_file.stem)
            all_songs.append(metadata)
    
    # Escanear raíz de music/
    if music_dir.exists() and music_dir.is_dir():
        for mp3_file in music_dir.glob("*.mp3"):
            metadata = get_mp3_metadata(mp3_file)
            metadata['playlist'] = None
            metadata['id'] = metadata.get('video_id', mp3_file.stem)
            all_songs.append(metadata)
    
    return all_songs


def find_song_by_video_id(music_dir: Path, video_id: str) -> Optional[Dict[str, str]]:
    """Busca una canción por su video_id en todo el directorio de música.
    
    Args:
        music_dir: Directorio raíz de música
        video_id: ID del video de YouTube
        
    Returns:
        Diccionario con información de la canción si existe, None en caso contrario
    """
    all_songs = scan_all_songs(music_dir)
    
    for song in all_songs:
        if song.get('video_id') == video_id:
            return song
    
    return None


def is_song_downloaded(music_dir: Path, video_id: str) -> bool:
    """Verifica si una canción ya está descargada buscando por video_id.
    
    Args:
        music_dir: Directorio raíz de música
        video_id: ID del video de YouTube
        
    Returns:
        True si la canción existe, False en caso contrario
    """
    return find_song_by_video_id(music_dir, video_id) is not None


def get_playlist_stats(music_dir: Path) -> Dict[str, int]:
    """Obtiene estadísticas de playlists.
    
    Args:
        music_dir: Directorio raíz de música
        
    Returns:
        Diccionario con nombre de playlist y cantidad de canciones
    """
    stats = {}
    playlists = scan_playlists(music_dir)
    
    for playlist in playlists:
        songs = scan_songs_in_playlist(music_dir, playlist)
        stats[playlist] = len(songs)
    
    return stats


def truncate_text(text: str, max_length: int = 30) -> str:
    """Trunca texto largo con puntos suspensivos.
    
    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        
    Returns:
        Texto truncado con "..." si es necesario
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
