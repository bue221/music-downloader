"""GUI moderna para Music Downloader.

Interfaz gráfica con diseño premium y animaciones.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from typing import Optional, Callable
import queue

from .cache import DownloadCache
from .youtube import YouTubeDownloader, YouTubeDownloadError


# Configuración de colores (Tema Oscuro Premium)
COLORS = {
    'bg_primary': '#0f0f23',      # Fondo principal oscuro
    'bg_secondary': '#1a1a2e',    # Fondo secundario
    'bg_card': '#16213e',         # Fondo de tarjetas
    'accent': '#e94560',          # Acento rojo vibrante
    'accent_hover': '#ff5577',    # Acento hover
    'text_primary': '#eaeaea',    # Texto principal
    'text_secondary': '#a0a0a0',  # Texto secundario
    'success': '#06ffa5',         # Verde éxito
    'warning': '#ffa500',         # Naranja advertencia
    'error': '#ff3838',           # Rojo error
    'border': '#2d2d44',          # Bordes
}

# Rutas base
PROJECT_ROOT = Path(__file__).parent.parent.parent
MUSIC_DIR = PROJECT_ROOT / "music"
CACHE_FILE = PROJECT_ROOT / ".downloaded.json"


class ModernButton(tk.Canvas):
    """Botón moderno con efectos hover y animaciones."""
    
    def __init__(self, parent, text: str, command: Callable, 
                 bg_color: str = COLORS['accent'], 
                 hover_color: str = COLORS['accent_hover'],
                 text_color: str = COLORS['text_primary'],
                 width: int = 200, height: int = 45):
        super().__init__(parent, width=width, height=height, 
                        bg=COLORS['bg_primary'], highlightthickness=0)
        
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.width = width
        self.height = height
        self.is_hovered = False
        
        # Dibujar botón
        self.draw_button()
        
        # Eventos
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)
        
    def draw_button(self):
        """Dibuja el botón con bordes redondeados."""
        self.delete('all')
        
        color = self.hover_color if self.is_hovered else self.bg_color
        
        # Rectángulo con bordes redondeados
        radius = 10
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, 
                                radius, fill=color, outline='')
        
        # Texto
        self.create_text(self.width//2, self.height//2, 
                        text=self.text, fill=self.text_color,
                        font=('SF Pro Display', 14, 'bold'))
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        """Crea un rectángulo con bordes redondeados."""
        points = [
            x1+radius, y1,
            x1+radius, y1,
            x2-radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def on_enter(self, event):
        """Efecto hover al entrar."""
        self.is_hovered = True
        self.draw_button()
        self.config(cursor='hand2')
        
    def on_leave(self, event):
        """Efecto hover al salir."""
        self.is_hovered = False
        self.draw_button()
        self.config(cursor='')
        
    def on_click(self, event):
        """Ejecuta el comando al hacer clic."""
        if self.command:
            self.command()


class MusicDownloaderGUI:
    """Interfaz gráfica principal del Music Downloader."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Music Downloader")
        self.root.geometry("900x700")
        self.root.configure(bg=COLORS['bg_primary'])
        self.root.resizable(False, False)
        
        # Configuraciones específicas para macOS
        try:
            # Traer la ventana al frente
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after_idle(self.root.attributes, '-topmost', False)
            
            # Forzar el foco en la ventana
            self.root.focus_force()
        except Exception:
            pass  # Ignorar si no es macOS o si hay problemas
        
        # Inicializar componentes
        self.cache = DownloadCache(CACHE_FILE)
        self.downloader: Optional[YouTubeDownloader] = None
        self.download_thread: Optional[threading.Thread] = None
        self.progress_queue = queue.Queue()
        
        # Variables
        self.url_var = tk.StringVar()
        self.playlist_name_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Listo para descargar")
        self.progress_var = tk.DoubleVar(value=0)
        
        # Construir UI
        self.build_ui()
        
        # Actualizar lista de canciones
        self.refresh_songs_list()
        
        # Iniciar verificación de progreso
        self.check_progress_queue()
        
        # Procesar eventos pendientes
        self.root.update()
        
    def build_ui(self):
        """Construye la interfaz de usuario."""
        # Header
        self.build_header()
        
        # Panel de descarga
        self.build_download_panel()
        
        # Panel de progreso
        self.build_progress_panel()
        
        # Panel de canciones
        self.build_songs_panel()
        
        # Footer
        self.build_footer()
        
    def build_header(self):
        """Construye el header con logo y título."""
        header_frame = tk.Frame(self.root, bg=COLORS['bg_primary'], height=100)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # Título con gradiente simulado
        title_label = tk.Label(
            header_frame,
            text="🎵 Music Downloader",
            font=('SF Pro Display', 32, 'bold'),
            fg=COLORS['accent'],
            bg=COLORS['bg_primary']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="Descarga música desde YouTube con estilo",
            font=('SF Pro Display', 12),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        subtitle_label.pack()
        
    def build_download_panel(self):
        """Construye el panel de descarga."""
        # Frame principal
        panel_frame = tk.Frame(self.root, bg=COLORS['bg_card'], 
                              highlightbackground=COLORS['border'],
                              highlightthickness=1)
        panel_frame.pack(fill='x', padx=20, pady=10)
        
        # Padding interno
        inner_frame = tk.Frame(panel_frame, bg=COLORS['bg_card'])
        inner_frame.pack(fill='both', padx=20, pady=20)
        
        # Título del panel
        tk.Label(
            inner_frame,
            text="📥 Nueva Descarga",
            font=('SF Pro Display', 18, 'bold'),
            fg=COLORS['text_primary'],
            bg=COLORS['bg_card']
        ).pack(anchor='w', pady=(0, 15))
        
        # URL Input
        url_frame = tk.Frame(inner_frame, bg=COLORS['bg_card'])
        url_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            url_frame,
            text="URL de YouTube:",
            font=('SF Pro Display', 11),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_card']
        ).pack(anchor='w')
        
        url_entry = tk.Entry(
            url_frame,
            textvariable=self.url_var,
            font=('SF Pro Display', 12),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief='flat',
            bd=0
        )
        url_entry.pack(fill='x', ipady=8, pady=(5, 0))
        
        # Nombre de playlist
        name_frame = tk.Frame(inner_frame, bg=COLORS['bg_card'])
        name_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            name_frame,
            text="Nombre de Playlist (opcional):",
            font=('SF Pro Display', 11),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_card']
        ).pack(anchor='w')
        
        name_entry = tk.Entry(
            name_frame,
            textvariable=self.playlist_name_var,
            font=('SF Pro Display', 12),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            insertbackground=COLORS['text_primary'],
            relief='flat',
            bd=0
        )
        name_entry.pack(fill='x', ipady=8, pady=(5, 0))
        
        # Botones
        buttons_frame = tk.Frame(inner_frame, bg=COLORS['bg_card'])
        buttons_frame.pack(fill='x')
        
        # Botón descargar
        self.download_btn = ModernButton(
            buttons_frame,
            text="⬇️ Descargar",
            command=self.start_download,
            width=180
        )
        self.download_btn.pack(side='left', padx=(0, 10))
        
        # Botón seleccionar archivo
        file_btn = ModernButton(
            buttons_frame,
            text="📁 Desde Archivo",
            command=self.select_file,
            bg_color=COLORS['bg_secondary'],
            hover_color=COLORS['border'],
            width=180
        )
        file_btn.pack(side='left')
        
    def build_progress_panel(self):
        """Construye el panel de progreso."""
        panel_frame = tk.Frame(self.root, bg=COLORS['bg_card'],
                              highlightbackground=COLORS['border'],
                              highlightthickness=1)
        panel_frame.pack(fill='x', padx=20, pady=10)
        
        inner_frame = tk.Frame(panel_frame, bg=COLORS['bg_card'])
        inner_frame.pack(fill='both', padx=20, pady=15)
        
        # Estado
        self.status_label = tk.Label(
            inner_frame,
            textvariable=self.status_var,
            font=('SF Pro Display', 11),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_card']
        )
        self.status_label.pack(anchor='w', pady=(0, 8))
        
        # Barra de progreso personalizada
        progress_bg = tk.Canvas(
            inner_frame,
            height=8,
            bg=COLORS['bg_secondary'],
            highlightthickness=0
        )
        progress_bg.pack(fill='x')
        
        self.progress_bar = progress_bg.create_rectangle(
            0, 0, 0, 8,
            fill=COLORS['success'],
            outline=''
        )
        self.progress_canvas = progress_bg
        
    def build_songs_panel(self):
        """Construye el panel de canciones descargadas."""
        panel_frame = tk.Frame(self.root, bg=COLORS['bg_card'],
                              highlightbackground=COLORS['border'],
                              highlightthickness=1)
        panel_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        inner_frame = tk.Frame(panel_frame, bg=COLORS['bg_card'])
        inner_frame.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Header con título y botón
        header = tk.Frame(inner_frame, bg=COLORS['bg_card'])
        header.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            header,
            text="📚 Canciones Descargadas",
            font=('SF Pro Display', 18, 'bold'),
            fg=COLORS['text_primary'],
            bg=COLORS['bg_card']
        ).pack(side='left')
        
        # Botón limpiar caché
        clear_btn = ModernButton(
            header,
            text="🗑️ Limpiar Caché",
            command=self.clear_cache,
            bg_color=COLORS['error'],
            hover_color='#ff5555',
            width=150,
            height=35
        )
        clear_btn.pack(side='right')
        
        # Lista de canciones con scrollbar
        list_frame = tk.Frame(inner_frame, bg=COLORS['bg_card'])
        list_frame.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, bg=COLORS['bg_secondary'])
        scrollbar.pack(side='right', fill='y')
        
        self.songs_listbox = tk.Listbox(
            list_frame,
            font=('SF Pro Display', 11),
            bg=COLORS['bg_secondary'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['accent'],
            selectforeground=COLORS['text_primary'],
            relief='flat',
            bd=0,
            yscrollcommand=scrollbar.set,
            highlightthickness=0
        )
        self.songs_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.songs_listbox.yview)
        
    def build_footer(self):
        """Construye el footer con estadísticas."""
        footer_frame = tk.Frame(self.root, bg=COLORS['bg_primary'])
        footer_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.stats_label = tk.Label(
            footer_frame,
            text="",
            font=('SF Pro Display', 10),
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_primary']
        )
        self.stats_label.pack()
        
        self.update_stats()
        
    def update_stats(self):
        """Actualiza las estadísticas del footer."""
        songs = self.cache.list_songs()
        total = len(songs)
        playlists = len(set(s.get('playlist', '') for s in songs if s.get('playlist')))
        
        self.stats_label.config(
            text=f"Total: {total} canciones | Playlists: {playlists}"
        )
        
    def refresh_songs_list(self):
        """Actualiza la lista de canciones."""
        self.songs_listbox.delete(0, tk.END)
        songs = self.cache.list_songs()
        
        if not songs:
            self.songs_listbox.insert(tk.END, "  No hay canciones descargadas")
            return
        
        for song in songs:
            artist = song.get('artist', 'Unknown')
            title = song.get('title', 'Unknown')
            playlist = f" [{song.get('playlist')}]" if song.get('playlist') else ""
            self.songs_listbox.insert(tk.END, f"  🎵 {artist} - {title}{playlist}")
            
        self.update_stats()
        
    def select_file(self):
        """Abre diálogo para seleccionar archivo de URLs."""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de URLs",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            # Pedir nombre de playlist
            if not self.playlist_name_var.get():
                messagebox.showwarning(
                    "Nombre requerido",
                    "Por favor, ingresa un nombre para la playlist antes de seleccionar el archivo."
                )
                return
            
            # Leer URLs del archivo
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]
                
                if urls:
                    self.url_var.set(f"{len(urls)} URLs cargadas desde archivo")
                    self.start_download_from_file(urls)
                else:
                    messagebox.showwarning("Archivo vacío", "El archivo no contiene URLs.")
            except Exception as e:
                messagebox.showerror("Error", f"Error leyendo archivo: {e}")
                
    def start_download(self):
        """Inicia la descarga desde URL."""
        url = self.url_var.get().strip()
        
        if not url or url.startswith("URLs cargadas"):
            messagebox.showwarning("URL requerida", "Por favor, ingresa una URL de YouTube.")
            return
        
        self.start_download_from_urls([url])
        
    def start_download_from_file(self, urls: list):
        """Inicia descarga desde lista de URLs."""
        self.start_download_from_urls(urls)
        
    def start_download_from_urls(self, urls: list):
        """Inicia el proceso de descarga en un hilo separado."""
        if self.download_thread and self.download_thread.is_alive():
            messagebox.showwarning("Descarga en progreso", "Ya hay una descarga en curso.")
            return
        
        # Deshabilitar botón
        self.download_btn.config(state='disabled')
        
        # Iniciar descarga en hilo
        self.download_thread = threading.Thread(
            target=self._download_worker,
            args=(urls,),
            daemon=True
        )
        self.download_thread.start()
        
    def _download_worker(self, urls: list):
        """Worker que ejecuta la descarga en segundo plano."""
        try:
            playlist_name = self.playlist_name_var.get().strip() or None
            custom_output_dir = None
            
            if playlist_name:
                custom_output_dir = MUSIC_DIR / "playlists" / playlist_name
            
            # Callback de progreso
            def on_progress(message: str):
                self.progress_queue.put(('status', message))
            
            # Crear downloader
            downloader = YouTubeDownloader(
                music_dir=MUSIC_DIR,
                cache=self.cache,
                on_progress=on_progress
            )
            
            all_results = []
            total_urls = len(urls)
            
            for idx, url in enumerate(urls, 1):
                self.progress_queue.put(('progress', (idx / total_urls) * 100))
                results = downloader.download(
                    url,
                    output_dir=custom_output_dir,
                    playlist_name=playlist_name
                )
                all_results.extend(results)
            
            # Resumen
            downloaded = sum(1 for r in all_results if not r.get('skipped') and not r.get('error'))
            skipped = sum(1 for r in all_results if r.get('skipped'))
            errors = sum(1 for r in all_results if r.get('error'))
            
            summary = f"✅ Descargadas: {downloaded} | ⏭️ Omitidas: {skipped}"
            if errors:
                summary += f" | ❌ Errores: {errors}"
            
            self.progress_queue.put(('complete', summary))
            
        except YouTubeDownloadError as e:
            self.progress_queue.put(('error', f"Error de descarga: {e}"))
        except Exception as e:
            self.progress_queue.put(('error', f"Error inesperado: {e}"))
            
    def check_progress_queue(self):
        """Verifica la cola de progreso y actualiza la UI."""
        try:
            while True:
                msg_type, data = self.progress_queue.get_nowait()
                
                if msg_type == 'status':
                    self.status_var.set(data)
                elif msg_type == 'progress':
                    self.update_progress_bar(data)
                elif msg_type == 'complete':
                    self.status_var.set(data)
                    self.update_progress_bar(100)
                    self.refresh_songs_list()
                    self.download_btn.config(state='normal')
                    self.url_var.set('')
                    messagebox.showinfo("Descarga completa", data)
                elif msg_type == 'error':
                    self.status_var.set(f"❌ {data}")
                    self.update_progress_bar(0)
                    self.download_btn.config(state='normal')
                    messagebox.showerror("Error", data)
                    
        except queue.Empty:
            pass
        
        # Programar siguiente verificación
        self.root.after(100, self.check_progress_queue)
        
    def update_progress_bar(self, percentage: float):
        """Actualiza la barra de progreso."""
        width = self.progress_canvas.winfo_width()
        new_width = (width * percentage) / 100
        self.progress_canvas.coords(self.progress_bar, 0, 0, new_width, 8)
        
    def clear_cache(self):
        """Limpia el caché de descargas."""
        result = messagebox.askyesno(
            "Confirmar",
            "¿Estás seguro de que quieres limpiar el caché?\n\nEsto no eliminará los archivos, solo el registro de descargas."
        )
        
        if result:
            self.cache.clear()
            self.refresh_songs_list()
            messagebox.showinfo("Caché limpiado", "El caché ha sido limpiado exitosamente.")
            
    def run(self):
        """Inicia la aplicación."""
        self.root.mainloop()


def launch_gui():
    """Función de entrada para lanzar la GUI."""
    app = MusicDownloaderGUI()
    app.run()


if __name__ == '__main__':
    launch_gui()
