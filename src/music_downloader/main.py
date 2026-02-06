"""CLI principal para Music Downloader.

Punto de entrada de la aplicación.
"""

import click
from pathlib import Path
from dotenv import load_dotenv

from .cache import DownloadCache
from .youtube import YouTubeDownloader, YouTubeDownloadError
from .spotify import SpotifyHandler, SpotifyDownloadError


# Cargar variables de entorno
load_dotenv()

# Rutas base
PROJECT_ROOT = Path(__file__).parent.parent.parent
MUSIC_DIR = PROJECT_ROOT / "music"
CACHE_FILE = PROJECT_ROOT / ".downloaded.json"


def print_status(message: str) -> None:
    """Imprime mensaje de estado."""
    click.echo(message)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Music Downloader - Descarga música desde YouTube y Spotify."""
    pass


@cli.command()
@click.option(
    '--platform', '-p',
    type=click.Choice(['youtube', 'spotify']),
    required=True,
    help='Plataforma de origen'
)
@click.option(
    '--url', '-u',
    required=False,
    help='URL de la canción o playlist'
)
@click.option(
    '--file', '-f',
    type=click.Path(exists=True, dir_okay=False),
    help='Archivo .txt con lista de URLs'
)
@click.option(
    '--name', '-n',
    help='Nombre de la carpeta de destino (obligatorio si usas --file)'
)
def download(platform: str, url: str, file: str, name: str):
    """Descarga música desde la plataforma especificada.
    
    \b
    Ejemplos:
      music-dl download -p youtube -u "https://youtube.com/watch?v=..."
      music-dl download -p spotify -f lista.txt -n "My Playlist"
    """
    if not url and not file:
        raise click.UsageError("Debes especificar --url o --file")
    
    if file and not name:
        raise click.UsageError("Debes especificar --name cuando usas --file")

    # Inicializar caché
    cache = DownloadCache(CACHE_FILE)
    
    # Recopilar URLs
    urls_to_process = []
    if url:
        urls_to_process.append(url)
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                urls_to_process.extend([line.strip() for line in f if line.strip()])
        except Exception as e:
            click.echo(f"❌ Error leyendo archivo: {e}", err=True)
            raise SystemExit(1)

    if not urls_to_process:
        click.echo("⚠️ No se encontraron URLs para procesar.")
        return

    # Configurar directorio de destino si se especifica nombre
    custom_output_dir = None
    if name:
        custom_output_dir = MUSIC_DIR / "playlists" / name
        click.echo(f"📂 Destino configurado: playlists/{name}")

    try:
        all_results = []
        
        if platform == 'youtube':
            downloader = YouTubeDownloader(
                music_dir=MUSIC_DIR,
                cache=cache,
                on_progress=print_status
            )
            
            for link in urls_to_process:
                results = downloader.download(
                    link,
                    output_dir=custom_output_dir,
                    playlist_name=name
                ) 
                all_results.extend(results)
            
        elif platform == 'spotify':
            try:
                handler = SpotifyHandler(
                    music_dir=MUSIC_DIR,
                    cache=cache,
                    on_progress=print_status
                )
                
                for link in urls_to_process:
                    results = handler.download(
                        link, 
                        output_dir=custom_output_dir, 
                        playlist_name=name
                    )
                    all_results.extend(results)
                    
        
        # Resumen
        downloaded = sum(1 for r in all_results if not r.get('skipped') and not r.get('error'))
        skipped = sum(1 for r in all_results if r.get('skipped'))
        errors = sum(1 for r in all_results if r.get('error'))
        
        click.echo("\n" + "=" * 40)
        click.echo(f"📊 Resumen Total:")
        click.echo(f"   ✅ Descargadas: {downloaded}")
        click.echo(f"   ⏭️  Omitidas: {skipped}")
        if errors:
            click.echo(f"   ❌ Errores: {errors}")
            
    except YouTubeDownloadError as e:
        click.echo(f"❌ Error de descarga: {e}", err=True)
        raise SystemExit(1)
    except SpotifyDownloadError as e:
        click.echo(f"❌ Error de Spotify: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"❌ Error inesperado: {e}", err=True)
        raise SystemExit(1)


@cli.command('list')
def list_songs():
    """Lista todas las canciones descargadas."""
    cache = DownloadCache(CACHE_FILE)
    songs = cache.list_songs()
    
    if not songs:
        click.echo("No hay canciones descargadas.")
        return
    
    click.echo(f"\n📚 Canciones descargadas ({len(songs)} total):\n")
    
    for song in songs:
        icon = "🎵" if song.get('source') == 'youtube' else "🎧"
        playlist = f" [{song.get('playlist')}]" if song.get('playlist') else ""
        click.echo(f"  {icon} {song.get('artist', 'Unknown')} - {song.get('title', 'Unknown')}{playlist}")


@cli.command('clear-cache')
def clear_cache():
    """Limpia el caché de descargas."""
    cache = DownloadCache(CACHE_FILE)
    cache.clear()
    click.echo("✅ Caché limpiado")


if __name__ == '__main__':
    cli()
