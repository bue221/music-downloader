# Music Downloader

CLI para descargar música desde YouTube y Spotify.

## Requisitos

- Python 3.11+
- ffmpeg (`brew install ffmpeg`)

## Instalación

```bash
make install
```

## Uso

```bash
# YouTube - canción individual
make download PLATFORM=youtube URL="https://www.youtube.com/watch?v=..."

# YouTube - playlist
make download PLATFORM=youtube URL="https://www.youtube.com/playlist?list=..."

# Spotify - playlist (requiere configuración de credenciales)
make download PLATFORM=spotify URL="https://open.spotify.com/playlist/..."

# Spotify - canción individual
make download PLATFORM=spotify URL="https://open.spotify.com/track/..."
```

## Configuración de Spotify

1. Crea una app en [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Copia `.env.example` a `.env`
3. Configura `SPOTIFY_CLIENT_ID` y `SPOTIFY_CLIENT_SECRET`
4. Si no quieren usar spotify pueden transferir sus listas gratis a youtube con esta herramienta y posteriormente descargar desde youtube https://www.tunemymusic.com/home

## Comandos Make

| Comando | Descripción |
|---------|-------------|
| `make install` | Instala dependencias |
| `make download` | Descarga música |
| `make list` | Lista canciones descargadas |
| `make clean-cache` | Limpia caché |
| `make help` | Muestra los comandos make disponibles |

## Uso Directo de CLI (`uv run music-dl`)

Para un control más granular y acceso a todas las funcionalidades, puedes ejecutar el CLI directamente usando `uv run music-dl`.

### Descargar Música

```bash
# Descargar una canción o playlist de YouTube/Spotify
uv run music-dl download --platform <youtube|spotify> --url <URL>

# Descargar canciones desde un archivo de texto, especificando el nombre de la carpeta de destino
uv run music-dl download --file <ruta/a/archivo.txt> --name <nombre_carpeta_destino>
```

### Listar Canciones Descargadas

```bash
uv run music-dl list
```

### Limpiar Caché

```bash
uv run music-dl clear-cache
```

### Mostrar Versión

```bash
uv run music-dl --version
```

