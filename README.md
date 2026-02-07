# 🎵 Music Downloader

Descargador de música desde YouTube con interfaz gráfica moderna y CLI potente.

## ✨ Características

- 🎨 **Interfaz Gráfica Premium** con tema oscuro y animaciones
- 🎯 **CLI Completa** para automatización y scripts
- 📦 **Descarga Individual** o por playlist
- 🗂️ **Organización Automática** en carpetas
- 💾 **Sistema de Caché** inteligente para evitar duplicados
- 🎼 **Conversión a MP3** con calidad 192kbps
- 📊 **Estadísticas** de descargas
- ⚡ **Descarga Asíncrona** en la GUI sin bloquear la interfaz

## 📋 Requisitos

- Python 3.13+
- ffmpeg (`brew install ffmpeg`)

## 🚀 Instalación

```bash
make install
```

---

## 🎨 Interfaz Gráfica (GUI)

### Características de la GUI

La GUI incluye un diseño moderno y premium con:

- **🌙 Tema Oscuro Premium**: Paleta de colores cuidadosamente seleccionada
- **✨ Botones Interactivos**: Efectos hover y animaciones suaves
- **📥 Descarga desde URL**: Ingresa directamente URLs de YouTube
- **📁 Descarga desde Archivo**: Carga múltiples URLs desde archivos .txt
- **📊 Barra de Progreso Animada**: Visualiza el progreso en tiempo real
- **📚 Lista de Canciones**: Ve todas tus canciones descargadas con scroll
- **🗑️ Gestión de Caché**: Limpia el caché con confirmación
- **📈 Estadísticas en Vivo**: Total de canciones y playlists

### Paleta de Colores

| Color | Código | Uso |
|-------|--------|-----|
| Fondo Principal | `#0f0f23` | Fondo de la ventana |
| Fondo Secundario | `#1a1a2e` | Inputs y elementos |
| Tarjetas | `#16213e` | Paneles |
| Acento Rojo | `#e94560` | Botones principales |
| Acento Verde | `#06ffa5` | Progreso y éxito |
| Texto Principal | `#eaeaea` | Texto |
| Texto Secundario | `#a0a0a0` | Subtítulos |

### Lanzar la GUI

```bash
# Opción 1: Usando Make
make gui

# Opción 2: Usando CLI directamente
uv run music-dl gui
```

---

## 💻 Uso de la CLI

### Comandos Disponibles

```bash
# Lanzar interfaz gráfica
uv run music-dl gui

# Descargar una canción o playlist
uv run music-dl download -u "https://www.youtube.com/watch?v=..."

# Descargar desde archivo de texto
uv run music-dl download -f lista.txt -n "Mi Playlist"

# Listar canciones descargadas
uv run music-dl list

# Limpiar caché
uv run music-dl clear-cache

# Mostrar versión
uv run music-dl --version

# Mostrar ayuda
uv run music-dl --help
```

### Comandos Make

| Comando | Descripción |
|---------|-------------|
| `make install` | Instala dependencias con uv |
| `make gui` | Lanza la interfaz gráfica |
| `make download URL=<url>` | Descarga música desde YouTube |
| `make list` | Lista canciones descargadas |
| `make clean-cache` | Limpia el caché |
| `make help` | Muestra comandos disponibles |

---

## 💾 Sistema de Caché

### ¿Cómo Funciona?

El sistema de caché utiliza el **`video_id` de YouTube** como identificador único global:

- ✅ **Evita descargas duplicadas** de la misma canción
- 📍 **Validación global**: Una canción solo se descarga una vez en todo el sistema
- 🗂️ **Registro en `.downloaded.json`**: Almacena metadata de cada descarga
- ⚡ **Verificación rápida**: Antes de descargar, verifica si ya existe

### Comportamiento

```
1. Primera descarga de "Bohemian Rhapsody" en carpeta "Rock"
   → ✅ Se descarga y registra con video_id: "fJ9rUzIMcZQ"

2. Intento de descargar la MISMA canción en carpeta "Favoritas"
   → ⏭️ SKIP - El caché detecta que ya existe
   → El archivo permanece solo en "Rock"
```

### Estructura del Caché

El archivo `.downloaded.json` contiene:

```json
{
  "songs": {
    "video_id_único": {
      "title": "Nombre de la canción",
      "artist": "Artista",
      "source": "youtube",
      "path": "/ruta/completa/al/archivo.mp3",
      "playlist": "Nombre de la playlist (opcional)",
      "downloaded_at": "2026-02-07T00:10:30.123456"
    }
  }
}
```

### Gestión del Caché

```bash
# Ver canciones en caché
uv run music-dl list

# Limpiar caché (no elimina archivos, solo el registro)
uv run music-dl clear-cache
```

---

## 📁 Estructura del Proyecto

```
los_temas/
├── .downloaded.json           # Caché de descargas
├── music/                     # Directorio de música
│   ├── playlists/            # Playlists organizadas
│   │   ├── Rock Classics/
│   │   ├── Workout Mix/
│   │   └── Chill Vibes/
│   └── singles/              # Canciones individuales
├── src/
│   └── music_downloader/
│       ├── __init__.py
│       ├── main.py           # CLI principal
│       ├── gui.py            # Interfaz gráfica
│       ├── youtube.py        # Lógica de descarga
│       ├── cache.py          # Sistema de caché
│       └── utils.py          # Utilidades
├── pyproject.toml            # Configuración del proyecto
├── Makefile                  # Comandos Make
└── README.md                 # Este archivo
```

---

## 📖 Ejemplos de Uso

### Ejemplo 1: Descargar una Canción Individual

```bash
uv run music-dl download -u "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Resultado:**
- Se descarga en `music/singles/`
- Se registra en el caché
- Formato: MP3 a 192kbps

### Ejemplo 2: Descargar una Playlist

```bash
uv run music-dl download -u "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
```

**Resultado:**
- Se crea carpeta `music/playlists/[Nombre de la Playlist]/`
- Todas las canciones se descargan en esa carpeta
- Se registran en el caché con el nombre de la playlist

### Ejemplo 3: Descargar desde Archivo de Texto

**Archivo `mis_favoritas.txt`:**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
https://www.youtube.com/watch?v=kJQP7kiw5Fk
```

**Comando:**
```bash
uv run music-dl download -f mis_favoritas.txt -n "Favoritas 2026"
```

**Resultado:**
- Se crea carpeta `music/playlists/Favoritas 2026/`
- Se descargan las 3 canciones
- Se registran en el caché

### Ejemplo 4: Usar la GUI

```bash
make gui
```

**Pasos en la GUI:**
1. Ingresa la URL de YouTube
2. (Opcional) Ingresa nombre de playlist
3. Presiona "⬇️ Descargar"
4. Observa el progreso en tiempo real
5. Ve las canciones descargadas en la lista

---

## 🏗️ Arquitectura

### Componentes Principales

1. **CLI (`main.py`)**: Punto de entrada, comandos Click
2. **GUI (`gui.py`)**: Interfaz gráfica con Tkinter
3. **YouTubeDownloader (`youtube.py`)**: Lógica de descarga con yt-dlp
4. **DownloadCache (`cache.py`)**: Sistema de caché persistente
5. **Utils (`utils.py`)**: Funciones auxiliares

### Flujo de Descarga

```
Usuario → CLI/GUI → YouTubeDownloader → yt-dlp → YouTube
                         ↓
                   DownloadCache
                         ↓
                   File System
```

---

## ❓ Preguntas Frecuentes

### ¿Puedo descargar la misma canción en varias carpetas?

No, el caché actual previene duplicados globalmente. Si intentas descargar la misma canción en otra carpeta, se omitirá. Esto ahorra espacio y ancho de banda.

### ¿Qué formato tienen las canciones descargadas?

MP3 a 192kbps, convertidas automáticamente desde el mejor audio disponible en YouTube.

### ¿Puedo usar esto sin la GUI?

Sí, la CLI es completamente funcional de forma independiente. La GUI es opcional.

### ¿Dónde se guardan las canciones?

- Canciones individuales: `music/singles/`
- Playlists: `music/playlists/[Nombre]/`

### ¿Cómo limpio el caché sin borrar archivos?

```bash
uv run music-dl clear-cache
```

Esto solo limpia el registro, los archivos MP3 permanecen intactos.

### ¿La GUI funciona en macOS?

Sí, la GUI está optimizada para macOS con configuraciones específicas para Tkinter.

---

## 🛠️ Desarrollo

### Ejecutar Tests

```bash
pytest
```

### Estructura de Código

- **SOLID**: Principios de diseño orientado a objetos
- **DRY**: Sin duplicación de código
- **Separación de responsabilidades**: Cada módulo tiene un propósito único
- **Type hints**: Tipado estático para mejor mantenibilidad

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request en el repositorio.

---

**Hecho con ❤️ y Python**
