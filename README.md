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

## Comandos Make

| Comando | Descripción |
|---------|-------------|
| `make install` | Instala dependencias |
| `make download` | Descarga música |
| `make list` | Lista canciones descargadas |
| `make clean-cache` | Limpia caché |
