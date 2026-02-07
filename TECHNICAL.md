# 📚 Documentación Técnica - Music Downloader

## Índice

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Sistema de Caché](#sistema-de-caché)
3. [Interfaz Gráfica (GUI)](#interfaz-gráfica-gui)
4. [API Interna](#api-interna)
5. [Flujos de Trabajo](#flujos-de-trabajo)

---

## Arquitectura del Sistema

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    Music Downloader                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐              ┌──────────────┐        │
│  │     CLI      │              │     GUI      │        │
│  │  (main.py)   │              │   (gui.py)   │        │
│  └──────┬───────┘              └──────┬───────┘        │
│         │                             │                 │
│         └─────────────┬───────────────┘                 │
│                       │                                  │
│              ┌────────▼────────┐                        │
│              │ YouTubeDownloader│                        │
│              │  (youtube.py)    │                        │
│              └────────┬────────┘                        │
│                       │                                  │
│         ┌─────────────┼─────────────┐                   │
│         │             │             │                    │
│    ┌────▼────┐   ┌───▼────┐   ┌───▼────┐              │
│    │  Cache  │   │ yt-dlp │   │ Utils  │              │
│    │(cache.py)│   │        │   │(utils.py)│            │
│    └─────────┘   └────────┘   └────────┘              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Responsabilidades por Módulo

#### `main.py` - CLI Principal
- Punto de entrada de la aplicación
- Define comandos Click: `download`, `list`, `clear-cache`, `gui`
- Maneja argumentos y opciones de línea de comandos
- Orquesta las operaciones de alto nivel

#### `gui.py` - Interfaz Gráfica
- Implementa la interfaz Tkinter
- Componente `ModernButton` para botones personalizados
- Clase `MusicDownloaderGUI` para la ventana principal
- Manejo de threading para descargas asíncronas
- Sistema de cola (Queue) para comunicación entre threads

#### `youtube.py` - Lógica de Descarga
- Clase `YouTubeDownloader` para gestionar descargas
- Integración con yt-dlp
- Detección automática de playlists vs videos individuales
- Extracción de metadata
- Conversión a MP3

#### `cache.py` - Sistema de Caché
- Clase `DownloadCache` para gestión de caché
- Persistencia en JSON
- Verificación de duplicados
- Registro de descargas

#### `utils.py` - Utilidades
- Sanitización de nombres de archivo
- Creación de directorios
- Detección de URLs de playlist
- Funciones auxiliares

---

## Sistema de Caché

### Estructura de Datos

```python
{
  "songs": {
    "video_id": {
      "title": str,
      "artist": str,
      "source": "youtube",
      "path": str,
      "playlist": Optional[str],
      "downloaded_at": str  # ISO 8601 format
    }
  }
}
```

### Flujo de Verificación

```
┌─────────────────────────────────────────────────────┐
│ 1. Usuario solicita descarga de URL                 │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 2. YouTubeDownloader extrae video_id con yt-dlp     │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 3. Cache.is_downloaded(video_id)?                   │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
    ┌───────┐          ┌────────┐
    │  SÍ   │          │   NO   │
    └───┬───┘          └───┬────┘
        │                  │
        ▼                  ▼
┌───────────────┐   ┌──────────────┐
│ 4a. SKIP      │   │ 4b. DOWNLOAD │
│ Retorna path  │   │ Registra en  │
│ existente     │   │ caché        │
└───────────────┘   └──────────────┘
```

### Métodos Principales

```python
class DownloadCache:
    def is_downloaded(self, song_id: str) -> bool:
        """Verifica si una canción ya fue descargada."""
        
    def get_path(self, song_id: str) -> Optional[str]:
        """Obtiene la ruta de una canción descargada."""
        
    def register(
        self,
        song_id: str,
        title: str,
        artist: str,
        source: str,
        path: str,
        playlist_name: Optional[str] = None
    ) -> None:
        """Registra una canción como descargada."""
        
    def list_songs(self) -> list[dict]:
        """Lista todas las canciones descargadas."""
        
    def clear(self) -> None:
        """Limpia todo el caché."""
```

---

## Interfaz Gráfica (GUI)

### Arquitectura de Threading

```
┌──────────────────────────────────────────────────────┐
│                   Main Thread                         │
│  ┌────────────────────────────────────────────────┐  │
│  │            Tkinter Event Loop                   │  │
│  │  - Renderizado de UI                            │  │
│  │  - Manejo de eventos de usuario                 │  │
│  │  - Actualización de widgets                     │  │
│  └────────────────┬───────────────────────────────┘  │
│                   │                                   │
│                   │ check_progress_queue() cada 100ms │
│                   │                                   │
│                   ▼                                   │
│  ┌────────────────────────────────────────────────┐  │
│  │           Progress Queue                        │  │
│  │  - Mensajes de estado                           │  │
│  │  - Porcentaje de progreso                       │  │
│  │  - Resultados finales                           │  │
│  └────────────────▲───────────────────────────────┘  │
└───────────────────┼──────────────────────────────────┘
                    │
                    │ put()
                    │
┌───────────────────┼──────────────────────────────────┐
│                   │         Worker Thread             │
│  ┌────────────────┴───────────────────────────────┐  │
│  │        _download_worker()                       │  │
│  │  - Ejecuta descargas en segundo plano           │  │
│  │  - Envía actualizaciones a la cola              │  │
│  │  - No bloquea la UI                             │  │
│  └─────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Componentes Personalizados

#### ModernButton

```python
class ModernButton(tk.Canvas):
    """Botón personalizado con:
    - Bordes redondeados
    - Efectos hover
    - Animaciones suaves
    - Cursor personalizado
    """
```

**Características:**
- Dibujado con Canvas para bordes redondeados
- Eventos: `<Enter>`, `<Leave>`, `<Button-1>`
- Colores configurables: bg_color, hover_color, text_color
- Dimensiones personalizables

### Paneles de la GUI

1. **Header Panel**
   - Título principal
   - Subtítulo descriptivo

2. **Download Panel**
   - Input para URL
   - Input para nombre de playlist
   - Botón "Descargar"
   - Botón "Desde Archivo"

3. **Progress Panel**
   - Label de estado
   - Barra de progreso animada

4. **Songs Panel**
   - Título "Canciones Descargadas"
   - Listbox con scroll
   - Botón "Limpiar Caché"

5. **Footer Panel**
   - Estadísticas (total de canciones y playlists)

---

## API Interna

### YouTubeDownloader

```python
class YouTubeDownloader:
    def __init__(
        self,
        music_dir: Path,
        cache: DownloadCache,
        on_progress: Optional[Callable[[str], None]] = None
    ):
        """Inicializa el downloader."""
        
    def download(
        self,
        url: str,
        output_dir: Optional[Path] = None,
        playlist_name: Optional[str] = None
    ) -> list[dict]:
        """Descarga música desde una URL de YouTube.
        
        Returns:
            Lista de diccionarios con info de canciones:
            [
                {
                    "id": str,
                    "title": str,
                    "artist": str,
                    "skipped": bool,
                    "path": str,
                    "error": Optional[str]
                }
            ]
        """
```

### Configuración de yt-dlp

```python
base_opts = {
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
        'User-Agent': 'Mozilla/5.0 ...',
        'Referer': 'https://www.youtube.com/',
    }
}
```

---

## Flujos de Trabajo

### Flujo 1: Descarga Individual desde CLI

```
Usuario ejecuta: uv run music-dl download -u "URL"
    │
    ▼
main.py: download(url="URL", file=None, name=None)
    │
    ▼
Inicializa DownloadCache y YouTubeDownloader
    │
    ▼
YouTubeDownloader.download(url)
    │
    ├─► is_playlist_url(url)? → NO
    │
    ▼
_download_single(url)
    │
    ├─► _extract_info(url) → {id, title, artist, ...}
    │
    ├─► cache.is_downloaded(video_id)?
    │   ├─► SÍ → Retorna {skipped: True}
    │   └─► NO → Continúa
    │
    ├─► Determina output_dir = music/singles/
    │
    ├─► yt-dlp.download(url)
    │
    ├─► cache.register(video_id, metadata)
    │
    └─► Retorna {id, title, artist, path}
```

### Flujo 2: Descarga de Playlist desde GUI

```
Usuario presiona "Descargar" en GUI
    │
    ▼
start_download_from_urls([url])
    │
    ├─► Valida entrada
    │
    ├─► Deshabilita botón
    │
    ├─► Crea Worker Thread
    │
    └─► Thread.start()
        │
        ▼
    _download_worker(urls)
        │
        ├─► Para cada URL:
        │   │
        │   ├─► progress_queue.put(('progress', %))
        │   │
        │   └─► downloader.download(url)
        │
        ├─► Calcula resumen
        │
        └─► progress_queue.put(('complete', summary))
            │
            ▼
        Main Thread: check_progress_queue()
            │
            ├─► Actualiza status_label
            │
            ├─► Actualiza progress_bar
            │
            ├─► refresh_songs_list()
            │
            ├─► Habilita botón
            │
            └─► Muestra messagebox
```

### Flujo 3: Descarga desde Archivo

```
Usuario ejecuta: uv run music-dl download -f lista.txt -n "Playlist"
    │
    ▼
main.py: download(url=None, file="lista.txt", name="Playlist")
    │
    ├─► Lee archivo línea por línea
    │
    ├─► urls_to_process = [url1, url2, url3, ...]
    │
    ├─► custom_output_dir = music/playlists/Playlist/
    │
    └─► Para cada URL en urls_to_process:
        │
        └─► downloader.download(
                url,
                output_dir=custom_output_dir,
                playlist_name="Playlist"
            )
```

---

## Manejo de Errores

### Jerarquía de Excepciones

```python
Exception
    └── YouTubeDownloadError
        ├── Error de extracción de info
        ├── Error de descarga
        └── Error de conversión
```

### Estrategia de Manejo

1. **CLI**: Captura excepciones y muestra mensajes con `click.echo()`
2. **GUI**: Captura excepciones y muestra `messagebox.showerror()`
3. **Worker Thread**: Envía errores a través de `progress_queue`

---

## Optimizaciones

### Caché
- Evita re-descargas innecesarias
- Ahorra ancho de banda
- Reduce tiempo de ejecución

### Threading en GUI
- Descargas no bloquean la interfaz
- UI permanece responsiva
- Actualizaciones en tiempo real

### yt-dlp
- Configuración optimizada para audio
- Headers personalizados para evitar bloqueos
- Extracción plana para playlists grandes

---

## Consideraciones de Seguridad

1. **Sanitización de nombres de archivo**: Previene path traversal
2. **Validación de URLs**: Solo acepta URLs de YouTube
3. **Manejo seguro de archivos**: Usa Path de pathlib
4. **No almacena credenciales**: No requiere autenticación

---

## Extensibilidad

### Agregar Nuevas Fuentes

Para agregar soporte a otras plataformas (ej. SoundCloud):

1. Crear nuevo módulo `soundcloud.py`
2. Implementar clase `SoundCloudDownloader`
3. Actualizar `main.py` para detectar tipo de URL
4. Agregar lógica de routing en `download()`

### Agregar Nuevos Formatos

Para soportar otros formatos de audio:

1. Modificar `postprocessors` en `_base_opts`
2. Actualizar extensión en `output_template`
3. Ajustar `cache.register()` para incluir formato

---

**Última actualización**: 2026-02-07
